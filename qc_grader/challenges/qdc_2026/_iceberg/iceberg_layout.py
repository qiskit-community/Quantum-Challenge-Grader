"""Placement of 21 [[4,2,2]] blocks on ``ibm_boston``, and the graphs derived from it.

The single source of truth is :data:`PLACEMENT` (which physical qubits each block owns)
plus the device coupling map. Everything else here is derived: per-block role
assignments, the bridge qubits, block adjacency, the physical annotation graph, and the
fanout routes for logical ZZ rotations.

Validation against the paper (all asserted in :func:`self_test`):

* every block induces a spider(1,1,3) in the coupling map
* 21 x 6 = 126 block qubits, plus 11 bridges = 137 active. Bridges 91 and 115 are an
  individually redundant pair for blocks 12-15, so any single circuit uses 136 - the
  paper's "up to 136 physical qubits" (see :func:`_check_active_counts`)
* block adjacency reproduces exactly the 35 pairs of Table ``tab:cost``
* the only pair with two connections is (14, 19), the paper's own example

Stdlib-only except for the two ``*_graph`` helpers, which import networkx locally.
Run ``python3 -m utils.iceberg_layout`` to execute the self-checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from types import MappingProxyType

from . import iceberg_device as device
from .iceberg_block import CONFIGURATIONS, LogicalBlock, ROLES


#: Physical qubits owned by each block. Ground truth, from the paper's Fig. 1b.
PLACEMENT = {
    0: [0, 1, 2, 3, 4, 16],
    1: [6, 7, 8, 9, 10, 17],
    2: [22, 23, 24, 25, 26, 37],
    3: [11, 12, 18, 30, 31, 32],
    4: [20, 21, 36, 40, 41, 42],
    5: [28, 29, 38, 48, 49, 50],
    6: [57, 65, 66, 67, 68, 77],
    7: [33, 34, 39, 52, 53, 54],
    8: [58, 70, 71, 72, 73, 74],
    9: [43, 44, 56, 62, 63, 64],
    10: [76, 80, 81, 82, 83, 84],
    11: [78, 86, 87, 88, 89, 90],
    12: [79, 92, 93, 94, 95, 99],
    13: [96, 100, 101, 102, 103, 104],
    14: [97, 106, 107, 108, 109, 118],
    15: [98, 110, 111, 112, 113, 114],
    16: [116, 120, 121, 122, 123, 124],
    17: [119, 130, 131, 132, 133, 134],
    18: [136, 140, 141, 142, 143, 144],
    19: [117, 125, 126, 127, 128, 137],
    20: [138, 148, 149, 150, 151, 152],
}

#: Bridge qubits: unused qubits that route between two blocks. Derived by requiring the
#: resulting block adjacency to equal :data:`TAB_COST_PAIRS` with no spurious pairs,
#: which picks these 11 uniquely. 91 and 115 both bridge blocks 12-15 and are
#: individually redundant, so a given schedule routes over only one of them and uses 136
#: active qubits. The remaining candidates (27, 85) touch two blocks but would create
#: adjacencies the paper does not use, so they stay unused.
BRIDGES = (5, 45, 47, 51, 61, 69, 91, 105, 115, 129, 147)

#: The 35 adjacent block pairs listed in Table ``tab:cost``. Used as a validator.
TAB_COST_PAIRS = frozenset(
    {
        (0, 1), (0, 2), (1, 3), (2, 4), (2, 9), (3, 5), (3, 7), (4, 9), (5, 6),
        (5, 7), (5, 8), (6, 8), (6, 9), (6, 11), (7, 8), (8, 11), (8, 12), (9, 10),
        (10, 13), (11, 12), (11, 14), (11, 15), (12, 15), (13, 14), (13, 16),
        (13, 19), (14, 15), (14, 17), (14, 19), (15, 17), (16, 18), (16, 19),
        (17, 19), (17, 20), (19, 20),
    }
)

#: The logical grid of Fig. 2a: ``row -> {column: (block, l)}``. Rows 1-5 span columns
#: 1-6, row 6 spans 0-6 and row 7 spans 0-4, so the footprint is grid-like but not
#: rectangular. Each block occupies two grid-adjacent cells.
FIG2A_GRID = {
    1: {1: (4, 1), 2: (2, 0), 3: (0, 1), 4: (1, 0), 5: (3, 0), 6: (7, 1)},
    2: {1: (4, 0), 2: (2, 1), 3: (0, 0), 4: (1, 1), 5: (3, 1), 6: (7, 0)},
    3: {1: (9, 1), 2: (9, 0), 3: (6, 0), 4: (6, 1), 5: (5, 1), 6: (5, 0)},
    4: {1: (10, 1), 2: (10, 0), 3: (11, 0), 4: (11, 1), 5: (8, 0), 6: (8, 1)},
    5: {1: (13, 0), 2: (13, 1), 3: (14, 0), 4: (14, 1), 5: (15, 0), 6: (12, 1)},
    6: {0: (18, 1), 1: (16, 1), 2: (19, 1), 3: (17, 0), 4: (17, 1), 5: (15, 1),
        6: (12, 0)},
    7: {0: (18, 0), 1: (16, 0), 2: (19, 0), 3: (20, 1), 4: (20, 0)},
}


@dataclass(frozen=True)
class LatticeCheck:
    """Result of comparing a :class:`LogicalLattice` against a :class:`Placement`.

    ``ok`` covers *structural* validity only - every site naming a real logical qubit,
    exactly once. Whether the device can implement each declared coupling is reported
    separately in ``realizable`` / ``unrealizable``, so that starting from an idealised
    lattice and being told what to drop is a usable workflow: a full square lattice on
    the paper's sites reports the four couplings of :data:`FIG2A_MISSING`, which is how
    that constant was derived.
    """

    unknown_blocks: tuple
    duplicate_sites: tuple
    missing_sites: tuple
    realizable: tuple
    unrealizable: tuple
    degree_out_of_range: tuple

    @property
    def ok(self):
        return not (self.unknown_blocks or self.duplicate_sites)

    def summary(self):
        lines = ["structurally %s" % ("ok" if self.ok else "INVALID")]
        if self.unknown_blocks:
            lines.append("  sites naming unknown blocks: %s" % (self.unknown_blocks,))
        if self.duplicate_sites:
            lines.append("  logical qubits placed twice: %s" % (self.duplicate_sites,))
        if self.missing_sites:
            lines.append(
                "  logical qubits absent from the lattice: %s" % (self.missing_sites,)
            )
        lines.append(
            "  couplings: %d realizable, %d unrealizable"
            % (len(self.realizable), len(self.unrealizable))
        )
        for u, v in self.unrealizable:
            lines.append(
                "    %s - %s  (blocks %s not device-adjacent)"
                % (u, v, tuple(sorted((u[0], v[0]))))
            )
        if self.degree_out_of_range:
            lines.append("  sites with degree outside 2..4: %s"
                         % (self.degree_out_of_range,))
        return "\n".join(lines)

    def __repr__(self):
        return "LatticeCheck(ok=%s, realizable=%d, unrealizable=%d)" % (
            self.ok, len(self.realizable), len(self.unrealizable)
        )


@dataclass(frozen=True)
class LogicalLattice:
    """The graph of the Hamiltonian to simulate: its sites and its couplings.

    A *site* is one logical qubit, identified by ``(block, l)`` with ``l in (0, 1)`` and
    located at an integer coordinate ``(row, col)``. :attr:`edges` holds the couplings,
    so the lattice is a complete graph specification - it is not inferred from the
    coordinates at use time, and a square lattice with links removed is a different
    lattice, not the same one with exceptions noted elsewhere.

    Build it with :meth:`from_sites` or :meth:`from_rows`, giving the couplings either as
    an explicit ``edges`` list or as nearest neighbors less an ``omit`` list, or take
    part of an existing lattice with :meth:`from_blocks`.

    This is the object to loop over when building circuits: :attr:`edges` are the ZZ
    terms and :meth:`nodes` the single-qubit terms. Turning each into gates is the
    placement's job - see :meth:`Placement.route`.
    """

    sites: MappingProxyType
    edges: tuple

    @classmethod
    def from_sites(cls, sites, edges=None, omit=()):
        """Build from ``{(row, col): (block, l)}`` plus the couplings.

        The couplings are the graph, and you specify them one of two ways:

        * ``edges`` - the complete edge list, verbatim
        * ``omit`` - orthogonal nearest neighbors *minus* these, which is how the
          paper's lattice is described: a square lattice with four links absent

        Passing neither gives the full nearest-neighbor lattice. Passing both is an
        error, since it would be ambiguous which wins.
        """
        if edges is not None and omit:
            raise ValueError("pass either edges= or omit=, not both")
        sites = {tuple(coord): tuple(node) for coord, node in sites.items()}
        for coord, node in sites.items():
            if len(coord) != 2 or not all(isinstance(c, int) for c in coord):
                raise ValueError("coordinate must be two ints, got %r" % (coord,))
            if len(node) != 2 or node[1] not in (0, 1):
                raise ValueError("site must be (block, l) with l in (0, 1), got %r"
                                 % (node,))
        if edges is None:
            dropped = {_canonical_edge(u, v) for u, v in omit}
            candidates = nearest_neighbor_edges(sites)
            edges = tuple(
                e for e in candidates if _canonical_edge(*e) not in dropped
            )
            unknown = dropped - {_canonical_edge(*e) for e in candidates}
            if unknown:
                raise ValueError(
                    "omit= names couplings that are not nearest neighbors: %s"
                    % sorted(unknown)
                )
        edges = tuple((tuple(u), tuple(v)) for u, v in edges)
        known = set(sites.values())
        for u, v in edges:
            if u not in known or v not in known:
                raise ValueError("edge %s - %s names a site not on the lattice" % (u, v))
        return cls(sites=MappingProxyType(dict(sorted(sites.items()))), edges=edges)

    @classmethod
    def from_rows(cls, rows, edges=None, omit=()):
        """Build from the picture-like ``{row: {col: (block, l)}}`` form."""
        return cls.from_sites(
            {(row, col): node for row, entries in rows.items()
             for col, node in entries.items()},
            edges=edges, omit=omit,
        )

    def from_blocks(self, blocks):
        """The sub-lattice on ``blocks``: their sites and the couplings among them.

        Sites keep their coordinates, and only couplings with both ends in ``blocks`` are
        kept, so a logical qubit can lose inter-block couplings (check
        :meth:`degrees`). For example ``FIG2A.from_blocks([16, 18, 19])``.
        """
        blocks = set(blocks)
        sites = {c: n for c, n in self.sites.items() if n[0] in blocks}
        edges = [(u, v) for u, v in self.edges if u[0] in blocks and v[0] in blocks]
        return LogicalLattice.from_sites(sites, edges=edges)

    def to_graph(self):
        """The lattice as a bare ``networkx.Graph``, with no placement attached.

        Use :meth:`Placement.logical_graph` instead when you want the routes as well.
        """
        import networkx as nx

        positions = self.positions()
        graph = nx.Graph(lattice=self)
        for node in self.nodes():
            graph.add_node(node, block=node[0], l=node[1], grid_pos=positions[node])
        for u, v in self.edges:
            graph.add_edge(u, v, kind="intra" if u[0] == v[0] else "inter")
        return graph

    # -- lookups ----------------------------------------------------------------

    def nodes(self):
        """Sites in coordinate order."""
        return tuple(self.sites[coord] for coord in sorted(self.sites))

    def coordinates(self):
        """Map ``(block, l) -> (row, col)``."""
        return {node: coord for coord, node in self.sites.items()}

    def coordinate(self, site):
        return self.coordinates()[tuple(site)]

    def site_at(self, coord):
        return self.sites[tuple(coord)]

    def positions(self, flip_y=True):
        """Map site -> ``(x, y)`` for plotting; rows run downward by default."""
        return {
            node: (float(col), -float(row) if flip_y else float(row))
            for (row, col), node in self.sites.items()
        }

    def intra_edges(self):
        return tuple((u, v) for u, v in self.edges if u[0] == v[0])

    def inter_edges(self):
        return tuple((u, v) for u, v in self.edges if u[0] != v[0])

    def degrees(self):
        degree = {node: 0 for node in self.nodes()}
        for u, v in self.edges:
            degree[u] += 1
            degree[v] += 1
        return degree

    def blocks(self):
        return tuple(sorted({node[0] for node in self.nodes()}))

    # -- consistency with a placement -------------------------------------------

    def realizable(self, placement):
        """Split :attr:`edges` into ``(realizable, unrealizable)`` for ``placement``.

        A coupling is realizable when both sites are in the same block, or their blocks
        are device-adjacent (directly or through a bridge).
        """
        adjacent = placement.adjacent_pairs()
        good, bad = [], []
        for u, v in self.edges:
            pair = tuple(sorted((u[0], v[0])))
            (good if u[0] == v[0] or pair in adjacent else bad).append((u, v))
        return tuple(good), tuple(bad)

    def check(self, placement):
        """Compare against a placement; returns a :class:`LatticeCheck`."""
        seen: dict = {}
        duplicates = []
        for coord in sorted(self.sites):
            node = self.sites[coord]
            if node in seen:
                duplicates.append((node, seen[node], coord))
            else:
                seen[node] = coord
        unknown = tuple(
            (coord, self.sites[coord]) for coord in sorted(self.sites)
            if self.sites[coord][0] not in placement.blocks
        )
        missing = tuple(
            node for node in placement.logical_nodes() if node not in seen
        )
        good, bad = self.realizable(placement)
        degree = self.degrees()
        out_of_range = tuple(
            (node, d) for node, d in sorted(degree.items()) if not 2 <= d <= 4
        )
        return LatticeCheck(
            unknown_blocks=unknown,
            duplicate_sites=tuple(duplicates),
            missing_sites=missing,
            realizable=good,
            unrealizable=bad,
            degree_out_of_range=out_of_range,
        )

    def __repr__(self):
        return "LogicalLattice(%d sites, %d couplings: %d intra + %d inter)" % (
            len(self.sites), len(self.edges),
            len(self.intra_edges()), len(self.inter_edges()),
        )


def _canonical_edge(u, v):
    """Order an edge's endpoints so it can be compared regardless of direction."""
    u, v = tuple(u), tuple(v)
    return (u, v) if u <= v else (v, u)


def nearest_neighbor_edges(sites):
    """Orthogonal nearest-neighbor couplings on integer coordinates."""
    edges = []
    for (row, col), node in sorted(sites.items()):
        for drow, dcol in ((0, 1), (1, 0)):
            other = sites.get((row + drow, col + dcol))
            if other is not None:
                edges.append((node, other))
    return tuple(edges)


#: The four square-lattice couplings absent from Fig. 2a. They are absent because the
#: placement cannot provide them - those block pairs are neither directly connected nor
#: bridged - which ``self_test`` verifies rather than assumes.
FIG2A_MISSING = (
    ((0, 0), (6, 0)),
    ((1, 1), (6, 1)),
    ((10, 0), (11, 0)),
    ((8, 0), (15, 0)),
)

#: The 66 couplings of Fig. 2a written out, 21 intra + 45 inter, in coordinate order.
#: Equivalent to nearest neighbors less :data:`FIG2A_MISSING` - ``self_test`` asserts the
#: two agree, so pick whichever reads better at the call site::
#:
#:     LogicalLattice.from_rows(FIG2A_GRID, edges=FIG2A_EDGES)   # include these
#:     LogicalLattice.from_rows(FIG2A_GRID, omit=FIG2A_MISSING)  # all but these
FIG2A_EDGES = (
    ((4, 1), (2, 0)), ((4, 1), (4, 0)), ((2, 0), (0, 1)), ((2, 0), (2, 1)),
    ((0, 1), (1, 0)), ((0, 1), (0, 0)), ((1, 0), (3, 0)), ((1, 0), (1, 1)),
    ((3, 0), (7, 1)), ((3, 0), (3, 1)), ((7, 1), (7, 0)), ((4, 0), (2, 1)),
    ((4, 0), (9, 1)), ((2, 1), (0, 0)), ((2, 1), (9, 0)), ((0, 0), (1, 1)),
    ((1, 1), (3, 1)), ((3, 1), (7, 0)), ((3, 1), (5, 1)), ((7, 0), (5, 0)),
    ((9, 1), (9, 0)), ((9, 1), (10, 1)), ((9, 0), (6, 0)), ((9, 0), (10, 0)),
    ((6, 0), (6, 1)), ((6, 0), (11, 0)), ((6, 1), (5, 1)), ((6, 1), (11, 1)),
    ((5, 1), (5, 0)), ((5, 1), (8, 0)), ((5, 0), (8, 1)), ((10, 1), (10, 0)),
    ((10, 1), (13, 0)), ((10, 0), (13, 1)), ((11, 0), (11, 1)), ((11, 0), (14, 0)),
    ((11, 1), (8, 0)), ((11, 1), (14, 1)), ((8, 0), (8, 1)), ((8, 1), (12, 1)),
    ((13, 0), (13, 1)), ((13, 0), (16, 1)), ((13, 1), (14, 0)), ((13, 1), (19, 1)),
    ((14, 0), (14, 1)), ((14, 0), (17, 0)), ((14, 1), (15, 0)), ((14, 1), (17, 1)),
    ((15, 0), (12, 1)), ((15, 0), (15, 1)), ((12, 1), (12, 0)), ((18, 1), (16, 1)),
    ((18, 1), (18, 0)), ((16, 1), (19, 1)), ((16, 1), (16, 0)), ((19, 1), (17, 0)),
    ((19, 1), (19, 0)), ((17, 0), (17, 1)), ((17, 0), (20, 1)), ((17, 1), (15, 1)),
    ((17, 1), (20, 0)), ((15, 1), (12, 0)), ((18, 0), (16, 0)), ((16, 0), (19, 0)),
    ((19, 0), (20, 1)), ((20, 1), (20, 0)),
)

#: The paper's logical graph of Fig. 2a: a square lattice on :data:`FIG2A_GRID` less the
#: four couplings in :data:`FIG2A_MISSING`. 66 edges = 21 intra + 45 inter.
FIG2A = LogicalLattice.from_rows(FIG2A_GRID, omit=FIG2A_MISSING)


#: Which fork leaf carries ``az`` (the other carries ``d0``). Fig. 1b cannot distinguish
#: them, so this is a convention: the lower physical index. It reproduces the known
#: orientation of block 0 (az right at 4, d0 down at 16). Per-block overrides go here
#: once the orientations are optimized against the RZZ depth table.
AZ_QUBITS: dict = {}


def fork_candidates(placement=None, topology=None):
    """Map block -> the two terminal qubits on its degree-3 vertex, lowest first.

    These are the only two choices for ``az`` (the other leaf becomes ``d0``), so this
    is what to consult before writing an ``az_qubits`` override. Fig. 1b of the paper
    cannot distinguish them, and the choice is not cosmetic: swapping ``d0`` and ``az``
    changes which logical operators are cheap, so it is one of the degrees of freedom
    the paper optimizes over (its ``o``/``l`` schedule parameters).
    """
    placement = PLACEMENT if placement is None else placement
    neighbors = device.as_topology(topology).neighbors
    candidates = {}
    for index, qubits in sorted(placement.items()):
        qubits = set(qubits)
        inner = {q: neighbors[q] & qubits for q in qubits}
        degree = {q: len(n) for q, n in inner.items()}
        hub = next(q for q, d in degree.items() if d == 3)
        candidates[index] = tuple(
            sorted(q for q in inner[hub] if degree[q] == 1)
        )
    return candidates


def assign_roles(qubits, az_leaf=None, topology=None):
    """Map role -> physical for a block, by walking its spider(1,1,3).

    The degree-3 site is ``d1``; its degree-2 neighbor starts the branch
    ``d2 -> d3 -> ax``; its two leaves are ``d0`` and ``az``. Which leaf is which is
    the convention documented on :data:`AZ_QUBITS`. ``topology`` accepts anything
    :func:`iceberg_device.as_topology` understands.
    """
    qubits = set(qubits)
    if len(qubits) != 6:
        raise ValueError("a block needs 6 qubits, got %d" % len(qubits))
    neighbors = device.as_topology(topology).neighbors
    inner = {q: neighbors[q] & qubits for q in qubits}
    degree = {q: len(n) for q, n in inner.items()}
    if sorted(degree.values()) != [1, 1, 1, 2, 2, 3]:
        raise ValueError("qubits %s do not induce a spider(1,1,3)" % sorted(qubits))

    d1 = next(q for q, d in degree.items() if d == 3)
    leaves = sorted(q for q in inner[d1] if degree[q] == 1)
    if len(leaves) != 2:
        raise ValueError("expected two fork leaves at %d, got %s" % (d1, leaves))
    d2 = next(q for q in inner[d1] if degree[q] == 2)
    d3 = next(q for q in inner[d2] if q != d1)
    ax = next(q for q in inner[d3] if q != d2)

    az = leaves[0] if az_leaf is None else az_leaf
    if az not in leaves:
        raise ValueError(
            "az_leaf %r is not one of this block's fork leaves %s; the two terminal "
            "qubits on the degree-3 vertex are the only valid choices "
            "(see fork_candidates())" % (az_leaf, leaves)
        )
    d0 = next(q for q in leaves if q != az)
    return {"d0": d0, "d1": d1, "d2": d2, "d3": d3, "ax": ax, "az": az}


@dataclass(frozen=True)
class Connection:
    """One physical link between two code blocks.

    Uniform across both cases: ``a_qubit`` and ``b_qubit`` are always the block qubits at
    the junction, and ``bridge`` is the routing qubit between them or ``None`` when the
    blocks touch directly. ``blocks`` is the sorted pair, so ``a_qubit`` belongs to
    ``blocks[0]``.
    """

    blocks: tuple
    a_qubit: int
    b_qubit: int
    bridge: int | None

    @property
    def kind(self):
        return "direct" if self.bridge is None else "bridge"

    @property
    def path(self):
        """Physical hops crossed by this connection, block qubit to block qubit."""
        if self.bridge is None:
            return (self.a_qubit, self.b_qubit)
        return (self.a_qubit, self.bridge, self.b_qubit)

    def roles(self, placement, frames=(0, 0)):
        """Role names of the two junction qubits, e.g. ``('az', 'd0')``."""
        a, b = self.blocks
        return (
            placement.blocks[a].role_at(self.a_qubit, frames[0]),
            placement.blocks[b].role_at(self.b_qubit, frames[1]),
        )

    def __repr__(self):
        if self.bridge is None:
            return "Connection(%d-%d direct: %d-%d)" % (
                self.blocks[0], self.blocks[1], self.a_qubit, self.b_qubit
            )
        return "Connection(%d-%d via %d: %d-%d-%d)" % (
            self.blocks[0], self.blocks[1], self.bridge,
            self.a_qubit, self.bridge, self.b_qubit,
        )


@dataclass(frozen=True)
class Route:
    """One fanout path realizing a logical ZZ rotation between two logical qubits.

    ``path`` is physical qubits in fanout order: the first two are one endpoint's
    logical-Z support, the last two the other's, with routing waypoints in between.
    ``roles`` labels each entry ``'a:<role>'``, ``'b:<role>'`` or ``'bridge'``, where
    ``a`` is whichever endpoint sorts lower.
    """

    u: tuple
    v: tuple
    path: tuple
    roles: tuple
    bridge: int | None
    supports: tuple
    frames: tuple
    signature: str

    @property
    def length(self):
        return len(self.path)

    def arms(self):
        """Decompose into ``(arm_a, arm_b, has_bridge)`` with side prefixes stripped.

        Each arm points inward: its logical-Z support first, then any routing waypoint
        toward the junction. Only eight distinct arm shapes occur across the whole
        placement, so the inter-block gadget is a pair of arms plus an optional bridge
        rather than a bespoke circuit per edge.
        """
        strip = lambda roles: tuple(r.split(":", 1)[1] for r in roles)
        arm_a = strip(r for r in self.roles if r.startswith("a:"))
        arm_b = strip(r for r in self.roles if r.startswith("b:"))
        return arm_a, tuple(reversed(arm_b)), "bridge" in self.roles

    @property
    def is_canonical(self):
        """Whether each arm is a support pair plus at most one ancilla waypoint.

        A CNOT ladder accumulates the Z value of every qubit it crosses, so a fanout may
        only be routed over spares - the bridge and the ``ax``/``az`` ancillas. Routes
        that walk across a block to reach its other logical-Z representative pick up
        those data qubits' Z and realize the wrong operator; they need two CNOTs per
        pass-through to fix, which is a different gadget rather than a deeper one.
        """
        if self.signature.startswith("intra:"):
            return True
        arm_a, arm_b, _ = self.arms()
        return all(
            len(arm) == 2 or (len(arm) == 3 and arm[2] in ("ax", "az"))
            for arm in (arm_a, arm_b)
        )

    def __repr__(self):
        return "Route(%s->%s, %s)" % (self.u, self.v, self.signature)


def _shortest_path(neighbors, start, goal, allowed, blocked=()):
    """BFS shortest path within ``allowed``, avoiding ``blocked``. None if unreachable."""
    if start == goal:
        return (start,)
    blocked = set(blocked)
    if start in blocked or goal in blocked:
        return None
    frontier = [(start,)]
    seen = {start} | blocked
    while frontier:
        nxt = []
        for path in frontier:
            for step in sorted(neighbors[path[-1]] & allowed):
                if step in seen:
                    continue
                extended = path + (step,)
                if step == goal:
                    return extended
                seen.add(step)
                nxt.append(extended)
        frontier = nxt
    return None


@dataclass(frozen=True)
class Placement:
    """A full placement: blocks, bridges, and the graphs derived from them."""

    blocks: dict
    bridges: tuple
    topology: device.Topology

    # -- construction -----------------------------------------------------------

    @classmethod
    def from_qubits(cls, placement=None, bridges=BRIDGES, az_qubits=None,
                    topology=None):
        """Build a placement.

        ``placement`` maps block index -> its six physical qubits and ``bridges`` lists
        the routing qubits; both default to the paper's values. ``topology`` fixes the
        backend connectivity and accepts a Qiskit ``CouplingMap``, a backend, an edge
        list, an :class:`iceberg_device.Topology`, or ``None`` for ``ibm_boston``.

        ``az_qubits`` sets the fork direction per block: ``{block: qubit}`` naming which
        terminal qubit on the degree-3 vertex carries ``az``, the other becoming ``d0``.
        Blocks left out follow the default convention (the lower-indexed leaf). Call
        :func:`fork_candidates` for the two valid choices per block, and
        :meth:`fork_choices` to read back what a placement ended up with.
        """
        placement = PLACEMENT if placement is None else placement
        az_qubits = AZ_QUBITS if az_qubits is None else az_qubits
        unknown = set(az_qubits) - set(placement)
        if unknown:
            raise ValueError("az_qubits names blocks not in the placement: %s"
                             % sorted(unknown))
        topology = device.as_topology(topology)
        blocks = {
            index: LogicalBlock(
                index, assign_roles(qubits, az_qubits.get(index), topology)
            )
            for index, qubits in sorted(placement.items())
        }
        return cls(blocks=blocks, bridges=tuple(sorted(bridges)), topology=topology)

    # -- basic lookups ----------------------------------------------------------

    def block(self, node):
        """The :class:`LogicalBlock` behind a logical node ``(b, l)`` or a block index."""
        return self.blocks[node[0] if isinstance(node, tuple) else node]

    def owner(self):
        """Map physical qubit -> owning block index (block qubits only)."""
        return {q: b for b, blk in self.blocks.items() for q in blk.physical_qubits()}

    def fork_choices(self):
        """Map block -> ``(d0, az)``, the fork direction each block ended up with.

        Feed this back through ``az_qubits`` to reproduce or perturb a placement::

            forks = place.fork_choices()
            tweaked = {b: d0 for b, (d0, az) in forks.items()}   # flip every block
            other = Placement.from_qubits(az_qubits=tweaked)
        """
        return {
            index: (block.qubits["d0"], block.qubits["az"])
            for index, block in sorted(self.blocks.items())
        }

    def logical_nodes(self):
        return tuple((b, l) for b in sorted(self.blocks) for l in (0, 1))

    def active_qubits(self):
        return frozenset(self.owner()) | frozenset(self.bridges)

    def unused_qubits(self):
        return frozenset(range(self.topology.n_qubits)) - self.active_qubits()

    # -- adjacency --------------------------------------------------------------

    def connections(self):
        """Map block pair -> tuple of :class:`Connection`.

        A pair may have more than one connection, which is the freedom the paper's
        ``w_e`` schedule parameter selects among.
        """
        owner = self.owner()
        found: dict = {}
        for u, v in self.topology.edges:
            if u in owner and v in owner and owner[u] != owner[v]:
                a, b = sorted((owner[u], owner[v]))
                a_qubit, b_qubit = (u, v) if owner[u] == a else (v, u)
                found.setdefault((a, b), []).append(
                    Connection((a, b), a_qubit, b_qubit, None)
                )
        neighbors = self.topology.neighbors
        for bridge in self.bridges:
            side: dict = {}
            for n in neighbors[bridge]:
                if n in owner:
                    side.setdefault(owner[n], []).append(n)
            for a, b in combinations(sorted(side), 2):
                if len(side[a]) != 1 or len(side[b]) != 1:
                    raise ValueError(
                        "bridge %d touches block %d/%d at more than one qubit: %r"
                        % (bridge, a, b, side)
                    )
                found.setdefault((a, b), []).append(
                    Connection((a, b), side[a][0], side[b][0], bridge)
                )
        return {pair: tuple(items) for pair, items in sorted(found.items())}

    def adjacent_pairs(self):
        return frozenset(self.connections())

    def bridges_between(self, a, b):
        pair = tuple(sorted((a, b)))
        return frozenset(
            c.bridge for c in self.connections().get(pair, ()) if c.bridge is not None
        )

    # -- routing ----------------------------------------------------------------

    def _adjacent(self, pair):
        return self.topology.adjacent(*pair)

    def routes(self, u, v, frames=(0, 0)):
        """Candidate fanout routes for a logical ZZ between nodes ``u`` and ``v``.

        Returns routes sorted shortest-first, empty if the pair is not adjacent or if
        neither logical-Z representative is an adjacent pair at the requested frames
        (which is exactly when a frame toggle is required).
        """
        if v < u:
            flipped = self.routes(v, u, (frames[1], frames[0]))
            return flipped
        (a, la), (b, lb) = u, v
        if a == b:
            return self._intra_routes(u, v, frames)
        if tuple(sorted((a, b))) not in self.connections():
            return ()

        block_a, block_b = self.blocks[a], self.blocks[b]
        neighbors = self.topology.neighbors
        allowed = (
            set(block_a.physical_qubits())
            | set(block_b.physical_qubits())
            | set(self.bridges_between(a, b))
        )
        owner = self.owner()

        out = {}
        for rep_a, support_a in enumerate(block_a.z_supports(la, frames[0])):
            if not self._adjacent(support_a):
                continue
            for rep_b, support_b in enumerate(block_b.z_supports(lb, frames[1])):
                if not self._adjacent(support_b):
                    continue
                for a_far, a_near in (support_a, support_a[::-1]):
                    for b_near, b_far in (support_b, support_b[::-1]):
                        middle = _shortest_path(
                            neighbors, a_near, b_near, allowed, blocked=(a_far, b_far)
                        )
                        if middle is None:
                            continue
                        path = (a_far,) + tuple(middle) + (b_far,)
                        if len(set(path)) != len(path):
                            continue
                        roles = tuple(
                            self._role_label(q, owner, a, b, frames) for q in path
                        )
                        bridge = next(
                            (q for q in path if q in self.bridges), None
                        )
                        signature = "-".join(roles)
                        out.setdefault(
                            path,
                            Route(
                                u=u, v=v, path=path, roles=roles, bridge=bridge,
                                supports=(support_a, support_b),
                                frames=frames, signature=signature,
                            ),
                        )
        return tuple(sorted(out.values(), key=lambda r: (r.length, r.path)))

    def frames_for(self, u, v):
        """The frames a coupling needs: ``(l_u, l_v)`` for inter, ``(0, 0)`` for intra.

        ``Zbar_1`` has no device-adjacent representative until ``SWAP(d1, d2)`` is
        applied, so logical qubit ``l`` requires its block at frame ``l``. Exactly one
        combination admits a route, so there is nothing to search over.
        """
        return (0, 0) if u[0] == v[0] else (u[1], v[1])

    def route(self, u, v):
        """The cheapest route for one coupling, choosing frames automatically.

        This is the entry point for circuit construction: loop over a
        :class:`LogicalLattice`'s couplings and call this for each. Returns ``None`` when
        the placement cannot implement the coupling.
        """
        found = self.routes(u, v, self.frames_for(u, v))
        return found[0] if found else None

    def connection_routes(self, u, v):
        """The realizable fanouts for one coupling: one per physical connection.

        Map :class:`Connection` -> :class:`Route`, shortest-first. Each connection fixes
        the junction qubit at both ends, which in turn pins the logical-Z representative
        each block must use, so exactly one :attr:`Route.is_canonical` route survives per
        connection. This is the ``w_e`` schedule freedom and the only per-edge choice:
        one option for most pairs, two where the blocks form a loop.

        Inter-block couplings only; returns ``{}`` for an intra-block pair, which has no
        connection to choose (use :meth:`route` for those).
        """
        by_path = {
            r.path: r
            for r in self.routes(u, v, self.frames_for(u, v))
            if r.is_canonical
        }
        chosen = {}
        for connection in self.connections().get(tuple(sorted((u[0], v[0]))), ()):
            crossed = set(connection.path)
            match = next(
                (r for p, r in by_path.items() if crossed <= set(p)), None
            )
            if match is not None:
                chosen[connection] = match
        return dict(sorted(chosen.items(), key=lambda kv: kv[1].length))

    def _intra_routes(self, u, v, frames):
        """Intra-block ZZ: Zbar_0 Zbar_1 = Z_d1 Z_d2, an adjacent pair at frame 0.

        The gadget structure (where R_Z sits, and the ancilla it uses) is deferred to
        the circuit-construction pass; this records the support only.
        """
        block = self.blocks[u[0]]
        pair = (block.physical("d1", frames[0]), block.physical("d2", frames[0]))
        if not self._adjacent(pair):
            return ()
        roles = ("a:d1", "a:d2")
        return (
            Route(
                u=u, v=v, path=pair, roles=roles, bridge=None,
                supports=(pair, pair), frames=frames,
                signature="intra:" + "-".join(roles),
            ),
        )

    def _role_label(self, qubit, owner, a, b, frames):
        if qubit in self.bridges:
            return "bridge"
        block_index = owner[qubit]
        side = "a" if block_index == a else "b"
        frame = frames[0] if block_index == a else frames[1]
        return "%s:%s" % (side, self.blocks[block_index].role_at(qubit, frame))

    def available_couplings(self):
        """Map block pair -> the four ``(l_a, l_b)`` logical couplings it could carry.

        The paper's Fig. 2a graph selects a 45-edge subset of these; that selection is
        a design choice recorded in the figure, not something the placement determines.
        """
        return {
            pair: tuple((la, lb) for la in (0, 1) for lb in (0, 1))
            for pair in sorted(self.connections())
        }

    # -- graphs -----------------------------------------------------------------

    def physical_graph(self, heron=None):
        """The device graph annotated with block/bridge/unused roles.

        ``heron`` controls the heavy-hex geometry (``row``, ``col``, ``pos``), which
        :mod:`iceberg_device` supplies rather than the coupling map, since a Qiskit
        ``CouplingMap`` carries no coordinates:

        * ``None`` (default) - attach it when the topology sits on the ibm_boston
          heavy-hex lattice, so a placement built from ``backend.coupling_map`` still
          draws correctly
        * ``True`` - attach it regardless, erroring if the qubit count disagrees
        * ``False`` - omit it, leaving plotting to compute a layout
        """
        if heron is None:
            heron = device.matches_heavy_hex(self.topology)
        elif heron and self.topology.n_qubits != device.N_QUBITS:
            raise ValueError(
                "heron=True needs %d qubits to match the heavy-hex lattice, got %d"
                % (device.N_QUBITS, self.topology.n_qubits)
            )

        import networkx as nx

        geometry = device.layout() if heron else {}
        graph = nx.Graph(name="placement", topology=self.topology)
        for qubit in range(self.topology.n_qubits):
            attrs = dict(geometry.get(qubit, {}))
            # 'kind' is reused below for usage, so keep the lattice type separately.
            attrs["lattice"] = attrs.pop("kind", None)
            graph.add_node(qubit, **attrs)
        graph.add_edges_from(self.topology.edges)
        owner = self.owner()
        for qubit in graph.nodes:
            if qubit in owner:
                index = owner[qubit]
                block = self.blocks[index]
                graph.nodes[qubit].update(
                    kind="block", block=index,
                    role=block.role_at(qubit),
                    syndrome_role=block.configured("syndrome")[qubit],
                )
            elif qubit in self.bridges:
                graph.nodes[qubit].update(kind="bridge", block=None, role=None)
            else:
                graph.nodes[qubit].update(kind="unused", block=None, role=None)
        for u, v in graph.edges:
            bu, bv = owner.get(u), owner.get(v)
            if bu is not None and bu == bv:
                kind = "intra_block"
            elif bu is not None and bv is not None:
                kind = "inter_block"
            elif u in self.bridges or v in self.bridges:
                kind = "bridge" if (bu is not None or bv is not None) else "unused"
            else:
                kind = "unused"
            graph.edges[u, v].update(kind=kind)
        return graph

    def logical_graph(self, lattice=None, frames=None):
        """Annotate a :class:`LogicalLattice` with the routes that implement it.

        ``lattice`` defaults to :data:`FIG2A`, the paper's logical graph. Only its
        *realizable* couplings become edges; the rest are recorded on the graph as
        ``missing_edges``. Nodes carry ``grid_pos`` from the lattice coordinates, and
        each edge carries the candidate :class:`Route` objects for it.

        ``frames`` defaults to choosing per edge via :meth:`frames_for`, which is the
        only choice that yields routes for every coupling. Pass an explicit pair to force
        one frame combination on every edge - useful for studying a schedule, but it will
        leave ``routes`` empty on any edge that combination cannot serve.
        """
        import networkx as nx

        lattice = FIG2A if lattice is None else lattice
        realizable, unrealizable = lattice.realizable(self)
        positions = lattice.positions()
        graph = nx.Graph(
            placement=self, lattice=lattice, missing_edges=unrealizable
        )
        for node in lattice.nodes():
            graph.add_node(node, block=node[0], l=node[1], grid_pos=positions[node])

        for u, v in realizable:
            graph.add_edge(
                u, v,
                kind="intra" if u[0] == v[0] else "inter",
                blocks=tuple(sorted((u[0], v[0]))),
                routes=self.routes(
                    u, v, self.frames_for(u, v) if frames is None else frames
                ),
            )
        return graph


# ---------------------------------------------------------------------------
# Self-checks
# ---------------------------------------------------------------------------


def _check_blocks_on_device(place):
    assert len(place.blocks) == 21, len(place.blocks)
    owner = place.owner()
    assert len(owner) == 126, len(owner)
    coupling = place.topology.edges
    for index, block in place.blocks.items():
        assert place.topology.induced_shape(block.physical_qubits()) == [1, 1, 1, 2, 2, 3], index
        for edge in block.physical_edges():
            assert edge in coupling, (index, edge)
        assert set(block.qubits) == set(ROLES), index


def _check_forks(place):
    candidates = fork_candidates()
    assert set(candidates) == set(place.blocks)
    for index, leaves in candidates.items():
        assert len(leaves) == 2 and leaves[0] < leaves[1], (index, leaves)
        block = place.blocks[index]
        # the default convention takes the lower leaf as az
        assert block.qubits["az"] == leaves[0], (index, leaves, block)
        assert {block.qubits["d0"], block.qubits["az"]} == set(leaves), index

    choices = place.fork_choices()
    assert choices[0] == (16, 4), choices[0]
    assert set(choices) == set(place.blocks)

    # Overriding one block flips exactly that fork and nothing else.
    flipped = Placement.from_qubits(az_qubits={0: 16})
    assert flipped.blocks[0].qubits["az"] == 16
    assert flipped.blocks[0].qubits["d0"] == 4
    assert flipped.blocks[0].physical_edges() == place.blocks[0].physical_edges()
    for index in place.blocks:
        if index != 0:
            assert flipped.fork_choices()[index] == choices[index], index

    # Round-trip: feeding fork_choices back reproduces the placement.
    same = Placement.from_qubits(az_qubits={b: az for b, (_, az) in choices.items()})
    assert same.fork_choices() == choices
    # Flipping every block gives the mirror image, and each block is still a valid spider.
    mirror = Placement.from_qubits(az_qubits={b: d0 for b, (d0, _) in choices.items()})
    for index, block in mirror.blocks.items():
        assert block.qubits["az"] == choices[index][0]
        assert place.topology.induced_shape(block.physical_qubits()) == [1, 1, 1, 2, 2, 3]

    # Bad input is rejected clearly.
    for bad, why in [({0: 3}, "a non-leaf qubit"), ({99: 4}, "an unknown block")]:
        try:
            Placement.from_qubits(az_qubits=bad)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for %s" % why)


def _check_block_zero(place):
    # The one orientation we know independently, from the RZZ depth table.
    block = place.blocks[0]
    assert block.qubits["az"] == 4, block
    assert block.qubits["d0"] == 16, block
    assert block.qubits["d1"] == 3, block
    assert block.configured("syndrome")[3] == "az"


def _check_active_counts(place):
    # 126 block qubits + 11 bridges. Bridges 91 and 115 both connect blocks 12 and 15
    # and are individually redundant - dropping either leaves all 66 lattice edges
    # routable on 136 qubits. Both are drawn in Fig. 1b, and the paper's "up to 136
    # physical qubits" is a per-circuit maximum, so only one is used by any schedule.
    assert len(place.bridges) == 11, place.bridges
    assert len(place.active_qubits()) == 137, len(place.active_qubits())
    assert len(place.unused_qubits()) == place.topology.n_qubits - 137
    owner = place.owner()
    assert not (set(place.bridges) & set(owner)), "a bridge cannot belong to a block"


def _check_adjacency(place):
    pairs = place.adjacent_pairs()
    assert pairs == TAB_COST_PAIRS, (
        sorted(pairs - TAB_COST_PAIRS), sorted(TAB_COST_PAIRS - pairs)
    )
    connections = place.connections()
    multi = {p: c for p, c in connections.items() if len(c) > 1}
    # (14, 19) is the paper's own example; (12, 15) is the other loop, and the only one
    # that carries lattice edges - (14, 19) is device-adjacent but unused by FIG2A.
    assert set(multi) == {(12, 15), (14, 19)}, multi
    assert all(len(c) == 2 for c in multi.values()), multi


def _check_routes(place):
    # Intra-block edge exists for every block at frame 0.
    for index in place.blocks:
        assert place.routes((index, 0), (index, 1)) != (), index

    # Every adjacent pair routes for (l_a, l_b) = (0, 0) at frame 0, since Zbar_0 always
    # has an adjacent-pair representative.
    for a, b in sorted(TAB_COST_PAIRS):
        found = place.routes((a, 0), (b, 0))
        assert found, (a, b)
        for route in found:
            assert len(set(route.path)) == len(route.path), route
            # a simple path on the device
            for x, y in zip(route.path, route.path[1:]):
                assert place.topology.adjacent(x, y), (route, x, y)
            assert sum(q in place.bridges for q in route.path) <= 1, route
            assert route.roles[0].startswith("a:") and route.roles[-1].startswith("b:")

    # Zbar_1 needs a frame toggle: no representative is adjacent at frame 0.
    a, b = 0, 1
    assert place.routes((a, 1), (b, 1), frames=(0, 0)) == ()
    assert place.routes((a, 1), (b, 1), frames=(1, 1)) != ()

    # Orientation independence: routing v->u mirrors u->v.
    assert place.routes((0, 0), (1, 0)) == place.routes((1, 0), (0, 0))

    # Non-adjacent blocks give nothing.
    assert (0, 20) not in TAB_COST_PAIRS
    assert place.routes((0, 0), (20, 0)) == ()

    # One canonical route per connection, and it is the shortest route through it.
    for a, b in sorted(TAB_COST_PAIRS):
        connections = place.connections()[(a, b)]
        for la in (0, 1):
            for lb in (0, 1):
                u, v = (a, la), (b, lb)
                chosen = place.connection_routes(u, v)
                assert len(chosen) == len(connections), (u, v, chosen)
                assert place.route(u, v) in chosen.values(), (u, v)
                for connection, route in chosen.items():
                    same = [
                        r for r in place.routes(u, v, place.frames_for(u, v))
                        if connection.bridge == r.bridge
                    ]
                    assert route.length == min(r.length for r in same), (u, v, route)


def cheapest_routes(place, frame_order=((0, 0), (1, 0), (0, 1), (1, 1))):
    """Shortest route for every ``(a, l_a, b, l_b)`` coupling, at the first frame that
    admits one. Returns a dict keyed by ``(u, v)``."""
    chosen = {}
    for a, b in sorted(TAB_COST_PAIRS):
        for la in (0, 1):
            for lb in (0, 1):
                u, v = (a, la), (b, lb)
                for frames in frame_order:
                    found = place.routes(u, v, frames)
                    if found:
                        chosen[(u, v)] = found[0]
                        break
    return chosen


def arm_shapes(place, routes=None):
    """Map arm shape -> occurrence count. Defaults to all 140 couplings' cheapest routes;
    pass ``routes`` (e.g. from :func:`lattice_routes`) to restrict to one lattice."""
    if routes is None:
        routes = cheapest_routes(place)
    shapes = {}
    for route in routes.values():
        if route.signature.startswith("intra:"):
            continue
        arm_a, arm_b, _ = route.arms()
        for arm in (arm_a, arm_b):
            shapes[arm] = shapes.get(arm, 0) + 1
    return shapes


def lattice_routes(place, lattice):
    """Shortest route for every edge of ``lattice``, keyed by the sorted edge.

    The frame pair is forced, not searched: :meth:`Placement.frames_for` is the unique
    feasible choice on every inter-block edge, and intra-block edges route at length 2
    in any frame, so the route returned is the global shortest in both cases (asserted
    in :func:`_check_lattice_routes`).

    The only real freedom is *which logical-Z representative* each endpoint uses --
    ``Zbar`` is defined modulo ``S_Z``, giving 2 x 2 = 4 candidates per inter-block edge.
    Across the paper's lattice the shortest of the four is unique on every edge, so this
    is a well-defined choice rather than a tie-break.
    """
    chosen = {}
    for u, v in lattice.to_graph().edges():
        edge = _canonical_edge(u, v)
        route = place.route(*edge)
        if route is not None:
            chosen[edge] = route
    return chosen


def route_templates(place, lattice=None, routes=None):
    """Map gadget template -> the lattice edges realized by it.

    A template is ``('intra', ('d1', 'd2'))`` or
    ``('direct' | 'bridge', (arm, arm))`` with the two arms sorted, so mirror-image
    routes share one template. Each arm points inward from its logical-Z support toward
    the junction, which is the order the CNOT fanout is applied in.
    """
    if routes is None:
        routes = lattice_routes(place, lattice)
    templates = {}
    for edge, route in routes.items():
        if route.signature.startswith("intra:"):
            key = ("intra", ("d1", "d2"))
        else:
            arm_a, arm_b, bridged = route.arms()
            key = ("bridge" if bridged else "direct", tuple(sorted((arm_a, arm_b))))
        templates.setdefault(key, []).append(edge)
    return {k: tuple(sorted(v)) for k, v in templates.items()}


def _check_topology(place):
    topology = place.topology
    assert topology is device.topology(), "default must be the cached ibm_boston"
    assert topology.n_qubits == 156 and len(topology.edges) == 176

    # as_topology accepts a Qiskit CouplingMap by duck-typing; stand in for one here so
    # the check runs without importing qiskit.
    class FakeCouplingMap:
        def size(self):
            return device.N_QUBITS
        def get_edges(self):                      # directed both ways, as Qiskit may be
            return [(v, u) for u, v in device.COUPLING_MAP] + list(device.COUPLING_MAP)

    from_cmap = device.as_topology(FakeCouplingMap())
    assert from_cmap.edges == topology.edges, "directed edges must symmetrise"
    assert from_cmap.coupling_map is not None

    # ... and a plain edge list, and an already-built Topology
    assert device.as_topology(device.COUPLING_MAP).edges == topology.edges
    assert device.as_topology(topology) is topology

    # A placement on an explicitly supplied topology behaves identically...
    explicit = Placement.from_qubits(topology=device.as_topology(device.COUPLING_MAP))
    assert explicit.adjacent_pairs() == place.adjacent_pairs()

    # ... and still recognizes the heavy-hex lattice, so it keeps its geometry even
    # though a CouplingMap carries no coordinates.
    assert device.matches_heavy_hex(from_cmap)
    assert device.matches_heavy_hex(explicit.topology)

    # A backend reporting fewer couplers than the ideal lattice still matches; one
    # reporting an edge the lattice lacks does not.
    fewer = device.topology_from_edges(
        device.N_QUBITS, sorted(topology.edges)[:-1]
    )
    assert device.matches_heavy_hex(fewer)
    extra = device.topology_from_edges(
        device.N_QUBITS, sorted(topology.edges) + [(0, 155)]
    )
    assert not device.matches_heavy_hex(extra)
    assert not device.matches_heavy_hex(device.topology_from_edges(4, [(0, 1), (1, 2)]))


def _check_lattice(place):
    lattice = FIG2A
    assert len(lattice.sites) == 42, len(lattice.sites)
    assert set(lattice.nodes()) == set(place.logical_nodes())
    assert len(lattice.edges) == 66, len(lattice.edges)
    assert len(lattice.intra_edges()) == 21, len(lattice.intra_edges())
    assert len(lattice.inter_edges()) == 45, len(lattice.inter_edges())
    # Each block occupies two lattice-adjacent cells, so every block appears once intra.
    assert {u[0] for u, _ in lattice.intra_edges()} == set(place.blocks)

    check = lattice.check(place)
    assert check.ok, check.summary()
    assert not check.unknown_blocks and not check.duplicate_sites
    assert not check.missing_sites, check.missing_sites
    assert len(check.realizable) == 66, len(check.realizable)
    assert not check.unrealizable, check.unrealizable
    assert not check.degree_out_of_range, check.degree_out_of_range

    # Every declared coupling can be routed at some frame.
    for u, v in check.realizable:
        assert any(place.routes(u, v, f) for f in ((0, 0), (1, 0), (0, 1), (1, 1))), (u, v)

    # FIG2A_MISSING is verified, not assumed: a *full* square lattice on these sites has
    # exactly those four couplings unrealizable, and each really fails to route.
    full = LogicalLattice.from_rows(FIG2A_GRID)
    assert len(full.edges) == 70, len(full.edges)
    full_check = full.check(place)
    assert {_canonical_edge(*e) for e in full_check.unrealizable} == {
        _canonical_edge(*e) for e in FIG2A_MISSING
    }, full_check.unrealizable
    for u, v in FIG2A_MISSING:
        assert place.route(u, v) is None, (u, v)

    # FIG2A_EDGES and omit=FIG2A_MISSING must describe the same graph, exactly.
    assert len(FIG2A_EDGES) == 66, len(FIG2A_EDGES)
    assert FIG2A_EDGES == lattice.edges, "FIG2A_EDGES has drifted from FIG2A"
    by_edges = LogicalLattice.from_rows(FIG2A_GRID, edges=FIG2A_EDGES)
    assert by_edges == lattice, "edges= and omit= must build the same lattice"
    assert by_edges.check(place).summary() == lattice.check(place).summary()

    # omit= must name real nearest-neighbor couplings.
    try:
        LogicalLattice.from_rows(FIG2A_GRID, omit=[((0, 0), (20, 0))])
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for a bogus omit= entry")
    try:
        LogicalLattice.from_rows(FIG2A_GRID, edges=[], omit=FIG2A_MISSING)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError when both edges= and omit= are given")

    # route() picks frames itself. Routes are returned in canonical orientation (the
    # lower-sorting endpoint is 'a'), so compare frames against the route's own ends.
    for u, v in check.realizable:
        auto = place.route(u, v)
        assert auto is not None, (u, v)
        assert auto.frames == place.frames_for(auto.u, auto.v), (u, v, auto)
        assert {auto.u, auto.v} == {u, v}, (u, v, auto)
        assert auto == place.routes(u, v, place.frames_for(u, v))[0]
        # orientation of the request must not matter
        assert place.route(v, u) == auto
    # logical_graph must give every edge a route: it has to pick frames per edge, not
    # apply one fixed pair (which would leave 36 of the 66 couplings empty).
    for u, v in lattice.edges:
        chosen = place.routes(u, v, place.frames_for(u, v))
        assert chosen, (u, v)
    fixed = [(u, v) for u, v in lattice.edges if not place.routes(u, v, (0, 0))]
    assert len(fixed) == 36, len(fixed)

    # Coordinates round-trip.
    for coord, node in lattice.sites.items():
        assert lattice.coordinate(node) == coord
        assert lattice.site_at(coord) == node

    # A user-supplied lattice: the 1D chain of six sites through blocks 4, 2, 0.
    chain_sites = {(0, i): node for i, node in enumerate(
        [(4, 1), (2, 0), (0, 1), (0, 0), (2, 1), (4, 0)])}
    chain = LogicalLattice.from_sites(chain_sites)
    assert len(chain.edges) == 5, chain.edges
    chain_check = chain.check(place)
    assert chain_check.ok, chain_check.summary()
    assert len(chain_check.missing_sites) == 36, len(chain_check.missing_sites)

    # Bad input is rejected rather than silently mis-built.
    for bad, why in [
        ({(0, 0): (0, 2)}, "l must be 0 or 1"),
        ({(0,): (0, 0)}, "coordinate must be a pair"),
    ]:
        try:
            LogicalLattice.from_sites(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError: %s" % why)
    try:
        LogicalLattice.from_sites({(0, 0): (0, 0)}, edges=[((0, 0), (9, 9))])
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for an edge naming an absent site")


def _check_arms(place):
    chosen = cheapest_routes(place)
    assert len(chosen) == 4 * len(TAB_COST_PAIRS) == 140, len(chosen)
    shapes = arm_shapes(place)
    assert len(shapes) == 8, sorted(shapes)
    # Every arm is its support pair, optionally followed by one ancilla waypoint.
    for arm in shapes:
        assert len(arm) in (2, 3), arm
        if len(arm) == 3:
            assert arm[2] in ("ax", "az"), arm


def _check_lattice_routes(place):
    """The paper's lattice routes completely, shortest-uniquely, from 8 arm shapes."""
    routes = lattice_routes(place, FIG2A)
    assert len(routes) == 66, len(routes)

    all_frames = ((0, 0), (1, 0), (0, 1), (1, 1))
    intra = {_canonical_edge(u, v) for u, v in FIG2A.intra_edges()}
    inter = {_canonical_edge(u, v) for u, v in FIG2A.inter_edges()}
    assert len(intra) == 21 and len(inter) == 45

    for edge, route in routes.items():
        candidates = place.routes(*edge, place.frames_for(*edge))
        shortest = min(r.length for r in candidates)
        # The chosen route is the unique shortest, and shortest over every frame too.
        assert route.length == shortest, edge
        assert sum(r.length == shortest for r in candidates) == 1, edge
        assert shortest == min(r.length for f in all_frames
                               for r in place.routes(*edge, f)), edge

        if edge in intra:
            # Frame-independent: SWAP(d1, d2) only relabels an adjacent pair.
            assert route.length == 2, edge
            assert all(place.routes(*edge, f)[0].length == 2 for f in all_frames), edge
        else:
            # Zbar_l needs frame l, so exactly one frame pair admits a route at all.
            feasible = {f for f in all_frames if place.routes(*edge, f)}
            assert feasible == {place.frames_for(*edge)}, (edge, sorted(feasible))
            # Four candidates per connection: the 2 x 2 logical-Z representative
            # freedom. Only one of the four is canonical, so the realizable count is
            # the connection count - see Placement.connection_routes.
            n_connections = len(place.connections()[tuple(sorted((edge[0][0], edge[1][0])))])
            assert len(candidates) == 4 * n_connections, (edge, len(candidates))
            assert len(place.connection_routes(*edge)) == n_connections, edge

    lengths = {}
    for route in routes.values():
        lengths[route.length] = lengths.get(route.length, 0) + 1
    assert lengths == {2: 21, 4: 7, 5: 19, 6: 11, 7: 8}, lengths

    # 66 edges collapse to 26 gadget templates built from only 8 arm shapes.
    templates = route_templates(place, routes=routes)
    assert len(templates) == 26, len(templates)
    assert sum(len(v) for v in templates.values()) == 66
    assert set(arm_shapes(place, routes)) == set(arm_shapes(place)), "new arm shape"
    assert len(arm_shapes(place, routes)) == 8


def self_test():
    place = Placement.from_qubits()
    _check_topology(place)
    _check_blocks_on_device(place)
    _check_block_zero(place)
    _check_forks(place)
    _check_active_counts(place)
    _check_adjacency(place)
    _check_routes(place)
    _check_lattice(place)
    _check_arms(place)
    _check_lattice_routes(place)
    return place


if __name__ == "__main__":
    placement = self_test()
    print("iceberg_layout: all self-checks passed")
    print("  21 blocks, %d block qubits, %d bridges, %d active, %d unused"
          % (len(placement.owner()), len(placement.bridges),
             len(placement.active_qubits()), len(placement.unused_qubits())))
    print("  %d adjacent block pairs == Table tab:cost" % len(placement.adjacent_pairs()))
    chosen = cheapest_routes(placement)
    print("  %d couplings routed, %d distinct full signatures"
          % (len(chosen), len({r.signature for r in chosen.values()})))
    check = FIG2A.check(placement)
    print("  %r" % (FIG2A,))
    print("  vs placement: %d realizable, %d unrealizable"
          % (len(check.realizable), len(check.unrealizable)))
    print("  %d distinct arm shapes:" % len(arm_shapes(placement)))
    for arm, count in sorted(arm_shapes(placement).items(), key=lambda kv: (len(kv[0]), kv[0])):
        print("      %3dx  %s" % (count, "-".join(arm)))
