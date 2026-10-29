"""``ibm_boston`` heavy-hex device geometry.

156 qubits: eight "long" rows of 16, interleaved with seven "connector" rows of 4.
Indices run row-major from the top-left, so long row ``k`` owns ``20k .. 20k+15`` and
the connector band below it owns ``20k+16 .. 20k+19``.

Connector columns alternate between bands: ``(3, 7, 11, 15)`` on even bands and
``(1, 5, 9, 13)`` on odd ones. The geometry is *generated* from that description and
then checked against :data:`COUPLING_MAP`, the coupling map reported by the backend,
so the two cannot silently disagree.

Stdlib-only by design (see :mod:`iceberg_block`). Run ``python3 -m utils.iceberg_device`` to
execute the self-checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType


LONG_ROW_WIDTH = 16
N_LONG_ROWS = 8
N_CONNECTOR_BANDS = N_LONG_ROWS - 1
QUBITS_PER_PERIOD = LONG_ROW_WIDTH + 4

#: Columns occupied by connector qubits, indexed by ``band % 2``.
CONNECTOR_COLUMNS = ((3, 7, 11, 15), (1, 5, 9, 13))

N_QUBITS = N_LONG_ROWS * LONG_ROW_WIDTH + N_CONNECTOR_BANDS * 4

#: Coupling map as reported for ``ibm_boston``. Ground truth; the generator below is
#: validated against it.
COUPLING_MAP = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (3, 16),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 8),
    (7, 17),
    (8, 9),
    (9, 10),
    (10, 11),
    (11, 12),
    (11, 18),
    (12, 13),
    (13, 14),
    (14, 15),
    (15, 19),
    (16, 23),
    (17, 27),
    (18, 31),
    (19, 35),
    (20, 21),
    (21, 22),
    (21, 36),
    (22, 23),
    (23, 24),
    (24, 25),
    (25, 26),
    (25, 37),
    (26, 27),
    (27, 28),
    (28, 29),
    (29, 30),
    (29, 38),
    (30, 31),
    (31, 32),
    (32, 33),
    (33, 34),
    (33, 39),
    (34, 35),
    (36, 41),
    (37, 45),
    (38, 49),
    (39, 53),
    (40, 41),
    (41, 42),
    (42, 43),
    (43, 44),
    (43, 56),
    (44, 45),
    (45, 46),
    (46, 47),
    (47, 48),
    (47, 57),
    (48, 49),
    (49, 50),
    (50, 51),
    (51, 52),
    (51, 58),
    (52, 53),
    (53, 54),
    (54, 55),
    (55, 59),
    (56, 63),
    (57, 67),
    (58, 71),
    (59, 75),
    (60, 61),
    (61, 62),
    (61, 76),
    (62, 63),
    (63, 64),
    (64, 65),
    (65, 66),
    (65, 77),
    (66, 67),
    (67, 68),
    (68, 69),
    (69, 70),
    (69, 78),
    (70, 71),
    (71, 72),
    (72, 73),
    (73, 74),
    (73, 79),
    (74, 75),
    (76, 81),
    (77, 85),
    (78, 89),
    (79, 93),
    (80, 81),
    (81, 82),
    (82, 83),
    (83, 84),
    (83, 96),
    (84, 85),
    (85, 86),
    (86, 87),
    (87, 88),
    (87, 97),
    (88, 89),
    (89, 90),
    (90, 91),
    (91, 92),
    (91, 98),
    (92, 93),
    (93, 94),
    (94, 95),
    (95, 99),
    (96, 103),
    (97, 107),
    (98, 111),
    (99, 115),
    (100, 101),
    (101, 102),
    (101, 116),
    (102, 103),
    (103, 104),
    (104, 105),
    (105, 106),
    (105, 117),
    (106, 107),
    (107, 108),
    (108, 109),
    (109, 110),
    (109, 118),
    (110, 111),
    (111, 112),
    (112, 113),
    (113, 114),
    (113, 119),
    (114, 115),
    (116, 121),
    (117, 125),
    (118, 129),
    (119, 133),
    (120, 121),
    (121, 122),
    (122, 123),
    (123, 124),
    (123, 136),
    (124, 125),
    (125, 126),
    (126, 127),
    (127, 128),
    (127, 137),
    (128, 129),
    (129, 130),
    (130, 131),
    (131, 132),
    (131, 138),
    (132, 133),
    (133, 134),
    (134, 135),
    (135, 139),
    (136, 143),
    (137, 147),
    (138, 151),
    (139, 155),
    (140, 141),
    (141, 142),
    (142, 143),
    (143, 144),
    (144, 145),
    (145, 146),
    (146, 147),
    (147, 148),
    (148, 149),
    (149, 150),
    (150, 151),
    (151, 152),
    (152, 153),
    (153, 154),
    (154, 155),
]


@dataclass(frozen=True)
class Topology:
    """Undirected device connectivity, resolved once.

    Backend-agnostic: build it from a Qiskit ``CouplingMap``, a backend, or a plain edge
    list via :func:`as_topology`. When a ``CouplingMap`` was supplied it is kept on
    :attr:`coupling_map` so the Qiskit object stays reachable.

    Coupling maps may be directed; ``edges`` is always symmetrised to sorted ``(u, v)``
    pairs, and ``neighbors`` is the undirected adjacency, built once rather than on
    every query.
    """

    n_qubits: int
    edges: frozenset
    neighbors: MappingProxyType
    coupling_map: object = field(default=None, compare=False)

    def adjacent(self, u, v):
        return (min(u, v), max(u, v)) in self.edges

    def degree(self, qubit):
        return len(self.neighbors[qubit])

    def induced_shape(self, qubits):
        """Sorted degree sequence of the subgraph induced on ``qubits``.

        A validly placed [[4,2,2]] block gives ``[1, 1, 1, 2, 2, 3]``.
        """
        qubits = set(qubits)
        return sorted(len(self.neighbors[q] & qubits) for q in qubits)

    def __len__(self):
        return self.n_qubits

    def __repr__(self):
        return "Topology(%d qubits, %d edges%s)" % (
            self.n_qubits,
            len(self.edges),
            "" if self.coupling_map is None else ", from CouplingMap",
        )


def topology_from_edges(n_qubits, pairs, coupling_map=None):
    """Build a :class:`Topology` from an iterable of qubit pairs."""
    edges = frozenset((min(u, v), max(u, v)) for u, v in pairs)
    neighbors = {q: set() for q in range(n_qubits)}
    for u, v in edges:
        neighbors[u].add(v)
        neighbors[v].add(u)
    return Topology(
        n_qubits=n_qubits,
        edges=edges,
        neighbors=MappingProxyType(
            {q: frozenset(n) for q, n in sorted(neighbors.items())}
        ),
        coupling_map=coupling_map,
    )


_IBM_BOSTON = None


def topology():
    """The cached :class:`Topology` for ``ibm_boston``."""
    global _IBM_BOSTON
    if _IBM_BOSTON is None:
        _IBM_BOSTON = topology_from_edges(N_QUBITS, COUPLING_MAP)
    return _IBM_BOSTON


def as_topology(source=None):
    """Coerce ``source`` to a :class:`Topology`.

    Accepts a :class:`Topology`, a Qiskit ``CouplingMap``, a backend (``BackendV2`` via
    ``.coupling_map``, ``BackendV1`` via ``.configuration().coupling_map``), an iterable
    of qubit pairs, or ``None`` for ``ibm_boston``. Qiskit is duck-typed, never imported.
    """
    if source is None:
        return topology()
    if isinstance(source, Topology):
        return source
    # Qiskit CouplingMap
    if hasattr(source, "get_edges") and hasattr(source, "size"):
        return topology_from_edges(
            source.size(), source.get_edges(), coupling_map=source
        )
    # Backend
    coupling = getattr(source, "coupling_map", None)
    if coupling is None and hasattr(source, "configuration"):
        coupling = getattr(source.configuration(), "coupling_map", None)
    if coupling is not None:
        return as_topology(coupling)
    # Plain edge list
    pairs = [tuple(pair) for pair in source]
    if not pairs:
        raise ValueError("cannot build a topology from an empty edge list")
    return topology_from_edges(1 + max(max(pair) for pair in pairs), pairs)


def matches_heavy_hex(candidate):
    """True when ``candidate`` sits on this module's heavy-hex lattice.

    Requires the same qubit count and edges that are a *subset* of the generated
    lattice - a backend may report fewer couplers than the ideal lattice (disabled
    edges) but must not report edges the lattice does not have. When this holds,
    :func:`layout` gives valid ``row``/``col``/``pos`` for every qubit, so a placement
    built from ``backend.coupling_map`` still draws as a heavy-hex device.

    All current Heron chips share the ``ibm_boston`` topology, so this is normally True.
    """
    return candidate.n_qubits == N_QUBITS and candidate.edges <= topology().edges


def long_row_qubit(row, col):
    """Physical index of the qubit at ``col`` in long row ``row``."""
    if not 0 <= row < N_LONG_ROWS:
        raise ValueError("long row out of range: %r" % (row,))
    if not 0 <= col < LONG_ROW_WIDTH:
        raise ValueError("column out of range: %r" % (col,))
    return QUBITS_PER_PERIOD * row + col


def connector_qubits(band):
    """Map column -> physical index for the connector qubits in ``band``."""
    if not 0 <= band < N_CONNECTOR_BANDS:
        raise ValueError("connector band out of range: %r" % (band,))
    base = QUBITS_PER_PERIOD * band + LONG_ROW_WIDTH
    return {col: base + j for j, col in enumerate(CONNECTOR_COLUMNS[band % 2])}


def layout():
    """Map physical index -> geometry dict with ``row``, ``col``, ``kind``, ``pos``.

    ``row`` counts long rows and is a half-integer for connector qubits, so that
    ``pos`` follows directly from ``(col, row)`` and draws as a heavy-hex lattice.
    """
    geometry = {}
    for row in range(N_LONG_ROWS):
        for col in range(LONG_ROW_WIDTH):
            qubit = long_row_qubit(row, col)
            geometry[qubit] = {
                "row": float(row),
                "col": col,
                "kind": "long",
                "pos": (float(col), -2.0 * row),
            }
    for band in range(N_CONNECTOR_BANDS):
        for col, qubit in connector_qubits(band).items():
            geometry[qubit] = {
                "row": band + 0.5,
                "col": col,
                "kind": "connector",
                "pos": (float(col), -2.0 * band - 1.0),
            }
    return geometry


def generated_edges():
    """Edge set implied by the geometry description, as sorted ``(u, v)`` tuples."""
    edges = set()
    for row in range(N_LONG_ROWS):
        for col in range(LONG_ROW_WIDTH - 1):
            edges.add((long_row_qubit(row, col), long_row_qubit(row, col + 1)))
    for band in range(N_CONNECTOR_BANDS):
        for col, qubit in connector_qubits(band).items():
            above = long_row_qubit(band, col)
            below = long_row_qubit(band + 1, col)
            edges.add((min(above, qubit), max(above, qubit)))
            edges.add((min(qubit, below), max(qubit, below)))
    return edges


def coupling_edges():
    """:data:`COUPLING_MAP` normalized to a set of sorted tuples."""
    return {(min(u, v), max(u, v)) for u, v in COUPLING_MAP}


def adjacency():
    """Map physical index -> frozenset of neighbors."""
    neighbors = {qubit: set() for qubit in layout()}
    for u, v in coupling_edges():
        neighbors[u].add(v)
        neighbors[v].add(u)
    return {q: frozenset(n) for q, n in neighbors.items()}


def degree():
    """Map physical index -> device degree."""
    return {q: len(n) for q, n in adjacency().items()}


def device_graph():
    """Return the device as a ``networkx.Graph`` annotated with :func:`layout` data."""
    import networkx as nx

    graph = nx.Graph(name="ibm_boston")
    for qubit, geometry in layout().items():
        graph.add_node(qubit, **geometry)
    graph.add_edges_from(coupling_edges())
    return graph


def induced_shape(qubits):
    """Degree sequence of the subgraph induced on ``qubits``, sorted ascending.

    A validly placed [[4,2,2]] block induces ``[1, 1, 1, 2, 2, 3]`` - the
    spider(1,1,3) of :mod:`iceberg_block`.
    """
    qubits = set(qubits)
    neighbors = adjacency()
    return sorted(len(neighbors[q] & qubits) for q in qubits)


# ---------------------------------------------------------------------------
# Self-checks
# ---------------------------------------------------------------------------


def _check_counts():
    geometry = layout()
    assert N_QUBITS == 156, N_QUBITS
    assert len(geometry) == N_QUBITS, len(geometry)
    assert set(geometry) == set(range(N_QUBITS)), "indices must be contiguous"
    long_qubits = [q for q, g in geometry.items() if g["kind"] == "long"]
    connectors = [q for q, g in geometry.items() if g["kind"] == "connector"]
    assert len(long_qubits) == N_LONG_ROWS * LONG_ROW_WIDTH == 128
    assert len(connectors) == N_CONNECTOR_BANDS * 4 == 28


def _check_generator_matches_backend():
    generated, reported = generated_edges(), coupling_edges()
    assert generated == reported, (
        "geometry disagrees with the backend coupling map: "
        "only generated %s, only reported %s"
        % (sorted(generated - reported), sorted(reported - generated))
    )
    assert len(reported) == 176, len(reported)


def _check_degrees():
    degrees = degree()
    assert max(degrees.values()) == 3, max(degrees.values())
    assert min(degrees.values()) == 1, min(degrees.values())
    # Every connector qubit bridges exactly two long rows.
    geometry = layout()
    for qubit, g in geometry.items():
        if g["kind"] == "connector":
            assert degrees[qubit] == 2, (qubit, degrees[qubit])


def _check_indexing_examples():
    # Spot-checks tying the index scheme to the reported coupling map.
    assert long_row_qubit(0, 0) == 0
    assert long_row_qubit(0, 15) == 15
    assert long_row_qubit(1, 0) == 20
    assert long_row_qubit(7, 15) == 155
    assert connector_qubits(0) == {3: 16, 7: 17, 11: 18, 15: 19}
    assert connector_qubits(1) == {1: 36, 5: 37, 9: 38, 13: 39}
    assert (3, 16) in coupling_edges() and (16, 23) in coupling_edges()


def _check_block_zero_shape():
    # Block 0 of the paper's placement: row-0 columns 0-4 plus the connector below
    # column 3. Must induce the spider(1,1,3) that a [[4,2,2]] block requires.
    assert induced_shape([0, 1, 2, 3, 4, 16]) == [1, 1, 1, 2, 2, 3]


def self_test():
    _check_counts()
    _check_generator_matches_backend()
    _check_degrees()
    _check_indexing_examples()
    _check_block_zero_shape()
    return True


if __name__ == "__main__":
    self_test()
    print(
        "iceberg_device: all self-checks passed "
        "(%d qubits, %d edges)" % (N_QUBITS, len(coupling_edges()))
    )
