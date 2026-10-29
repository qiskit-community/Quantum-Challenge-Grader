"""Site model and ``LogicalBlock`` for the [[4,2,2]] Iceberg code.

Follows Froland et al., arXiv:2607.24947 (see ``doc/Paper_Device_422.tex``).

A block occupies six physical qubits: data ``d0``-``d3`` plus ancillas ``ax``, ``az``.
The six sites form a fixed tree on the heavy-hex lattice - a "spider(1,1,3)": one
degree-3 site with two leaf branches and one three-site branch. That is the paper's
"one degree-3 vertex and two degree-2 vertices". The *compute* and *syndrome*
configurations are two role assignments over those same six sites, which is why
switching between them is a SWAP network rather than a re-embedding.

This module is deliberately stdlib-only so the data model can be imported and
self-checked without networkx or matplotlib. Graph construction lives elsewhere.

Run ``python3 -m utils.iceberg_block`` to execute the self-checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType


ROLES = ("d0", "d1", "d2", "d3", "ax", "az")
DATA_ROLES = ("d0", "d1", "d2", "d3")
ANCILLA_ROLES = ("ax", "az")

# Site geometry. Sites are positional only; which qubit occupies each depends on the
# configuration. Positions are for drawing.
#
#     s0 --- s1 --- s2
#             |
#            s3
#             |
#     s5 --- s4
#
SITE_POS = {
    0: (0.0, 2.0),
    1: (1.0, 2.0),
    2: (2.0, 2.0),
    3: (1.0, 1.0),
    4: (1.0, 0.0),
    5: (0.0, 0.0),
}

SITE_EDGES = ((0, 1), (1, 2), (1, 3), (3, 4), (4, 5))

#: The unique degree-3 site. Holds ``d1`` in the compute configuration, ``az`` in the
#: syndrome configuration.
DEGREE3_SITE = 1

#: The two leaf sites hanging off :data:`DEGREE3_SITE`. Fig. 1b of the paper cannot
#: distinguish them, so which is which is a placement convention - see
#: :data:`LogicalBlock.qubits`.
FORK_SITES = (0, 2)

CONFIGURATIONS = {
    "compute": {0: "d0", 1: "d1", 2: "az", 3: "d2", 4: "d3", 5: "ax"},
    "syndrome": {0: "d0", 1: "az", 2: "d1", 3: "ax", 4: "d2", 5: "d3"},
}

#: Stabilizers, both supported on all four data qubits: S_X = X0X1X2X3, S_Z = Z0Z1Z2Z3.
STABILIZER_SUPPORT = DATA_ROLES

# Logical operators, Eq. (2): Zbar_i = Z_d0 Z_d(i+1), Xbar_i = X_d(i+1) X_d3.
# Each has two representatives, related by multiplying through by the corresponding
# stabilizer, e.g. Zbar_0 = Z_d0 Z_d1 = Z_d2 Z_d3. Either may be used to evaluate the
# observable or to accumulate parity, so a router should try both and keep the cheaper.
Z_SUPPORTS = {
    0: (("d0", "d1"), ("d2", "d3")),
    1: (("d0", "d2"), ("d1", "d3")),
}

X_SUPPORTS = {
    0: (("d1", "d3"), ("d0", "d2")),
    1: (("d2", "d3"), ("d0", "d1")),
}

#: Frame f=1 means SWAP(d1, d2) has been applied relative to f=0. In the compute
#: configuration Zbar_(b,0) and Xbar_(b,1) are direct; Zbar_(b,1) and Xbar_(b,0) need
#: the toggle, because neither of their representatives is an adjacent pair.
FRAME_SWAP = ("d1", "d2")


def other_role(role):
    """Return the role a given role is exchanged with by a frame toggle."""
    if role == FRAME_SWAP[0]:
        return FRAME_SWAP[1]
    if role == FRAME_SWAP[1]:
        return FRAME_SWAP[0]
    return role


def site_of_role(role, configuration="compute"):
    """Return the site index holding ``role`` in ``configuration``."""
    for site, assigned in CONFIGURATIONS[configuration].items():
        if assigned == role:
            return site
    raise KeyError(role)


def anticommute(support_a, support_b):
    """True if two Pauli supports of different type (X vs Z) anticommute."""
    return len(set(support_a) & set(support_b)) % 2 == 1


@dataclass(frozen=True)
class LogicalBlock:
    """One [[4,2,2]] block placed on specific physical qubits.

    ``qubits`` maps each role in :data:`ROLES` to a physical qubit index, given in the
    **compute** configuration and at **frame 0**. Frame and configuration are circuit
    state, not layout, so they are arguments to the methods here rather than fields -
    one block instance is reused across every Trotter step.

    Instances are immutable but intentionally not hashable: blocks are never used as
    graph nodes (logical-graph nodes are ``(block, l)`` tuples), they live in one
    registry and are reached by index.
    """

    index: int
    qubits: dict

    def __post_init__(self):
        missing = set(ROLES) - set(self.qubits)
        extra = set(self.qubits) - set(ROLES)
        if missing or extra:
            raise ValueError(
                "block %r roles: missing %s, unexpected %s"
                % (self.index, sorted(missing), sorted(extra))
            )
        physical = list(self.qubits.values())
        if len(set(physical)) != len(ROLES):
            raise ValueError(
                "block %r maps two roles onto one physical qubit: %r"
                % (self.index, self.qubits)
            )
        object.__setattr__(
            self, "qubits", MappingProxyType({r: self.qubits[r] for r in ROLES})
        )

    # -- role <-> physical -------------------------------------------------------

    def physical(self, role, frame=0):
        """Physical qubit currently holding ``role``, accounting for the frame."""
        return self.qubits[other_role(role) if frame else role]

    def role_at(self, physical, frame=0):
        """Inverse of :meth:`physical`; None if the qubit is not in this block."""
        for role in ROLES:
            if self.physical(role, frame) == physical:
                return role
        return None

    def physical_qubits(self):
        """All six physical qubits, in :data:`ROLES` order (frame independent)."""
        return tuple(self.qubits[r] for r in ROLES)

    def configured(self, configuration="compute", frame=0):
        """Map physical qubit -> role label under ``configuration``."""
        return {
            self.physical(CONFIGURATIONS["compute"][site], frame): role
            for site, role in CONFIGURATIONS[configuration].items()
        }

    # -- topology ---------------------------------------------------------------

    def physical_edges(self):
        """The five physical edges spanned by this block (frame independent)."""
        compute = CONFIGURATIONS["compute"]
        edges = []
        for u, v in SITE_EDGES:
            a = self.qubits[compute[u]]
            b = self.qubits[compute[v]]
            edges.append((min(a, b), max(a, b)))
        return tuple(sorted(edges))

    def site_to_physical(self):
        """Map site index -> physical qubit."""
        compute = CONFIGURATIONS["compute"]
        return {site: self.qubits[compute[site]] for site in SITE_POS}

    # -- logical operator supports ----------------------------------------------

    def z_supports(self, l, frame=0):  # noqa: E741
        """Both physical supports of Zbar_l, stabilizer-equivalent representatives."""
        return tuple(
            tuple(self.physical(r, frame) for r in roles) for roles in Z_SUPPORTS[l]
        )

    def x_supports(self, l, frame=0):  # noqa: E741
        """Both physical supports of Xbar_l."""
        return tuple(
            tuple(self.physical(r, frame) for r in roles) for roles in X_SUPPORTS[l]
        )

    def z_support(self, l, frame=0, representative=0):  # noqa: E741
        """One physical support of Zbar_l."""
        return self.z_supports(l, frame)[representative]

    def x_support(self, l, frame=0, representative=0):  # noqa: E741
        """One physical support of Xbar_l."""
        return self.x_supports(l, frame)[representative]

    def stabilizer_support(self):
        """The four data qubits, carrying both S_X and S_Z (frame independent)."""
        return tuple(self.qubits[r] for r in DATA_ROLES)

    def __repr__(self):
        inner = ", ".join("%s=%d" % (r, self.qubits[r]) for r in ROLES)
        return "LogicalBlock(%d: %s)" % (self.index, inner)


def block_from_sites(index, site_to_physical):
    """Build a block from a site -> physical map, as figure extraction produces it."""
    compute = CONFIGURATIONS["compute"]
    return LogicalBlock(
        index=index,
        qubits={compute[site]: q for site, q in site_to_physical.items()},
    )


# ---------------------------------------------------------------------------
# Self-checks
# ---------------------------------------------------------------------------


def _check_site_graph():
    degree = {site: 0 for site in SITE_POS}
    for u, v in SITE_EDGES:
        degree[u] += 1
        degree[v] += 1
    assert len(SITE_POS) == 6, SITE_POS
    assert len(SITE_EDGES) == 5, SITE_EDGES
    assert sorted(degree.values()) == [1, 1, 1, 2, 2, 3], degree
    assert degree[DEGREE3_SITE] == 3
    assert all(degree[s] == 1 for s in FORK_SITES)
    # A tree: |E| == |V| - 1 and connected.
    seen, stack = {0}, [0]
    adjacency = {s: set() for s in SITE_POS}
    for u, v in SITE_EDGES:
        adjacency[u].add(v)
        adjacency[v].add(u)
    while stack:
        for nxt in adjacency[stack.pop()] - seen:
            seen.add(nxt)
            stack.append(nxt)
    assert seen == set(SITE_POS), seen


def _check_configurations():
    for name, mapping in CONFIGURATIONS.items():
        assert set(mapping) == set(SITE_POS), name
        assert sorted(mapping.values()) == sorted(ROLES), name
    # The degree-3 site holds d1 when computing and az when extracting syndromes.
    assert CONFIGURATIONS["compute"][DEGREE3_SITE] == "d1"
    assert CONFIGURATIONS["syndrome"][DEGREE3_SITE] == "az"
    # d0 is the only role that does not move between configurations.
    unmoved = [
        site
        for site in SITE_POS
        if CONFIGURATIONS["compute"][site] == CONFIGURATIONS["syndrome"][site]
    ]
    assert [CONFIGURATIONS["compute"][s] for s in unmoved] == ["d0"], unmoved


def _check_operator_algebra():
    # The two representatives of each logical differ by the stabilizer, so their
    # symmetric difference is the full four-qubit stabilizer support.
    for supports in (Z_SUPPORTS, X_SUPPORTS):
        for lq, (rep_a, rep_b) in supports.items():
            assert set(rep_a) ^ set(rep_b) == set(STABILIZER_SUPPORT), (
                lq,
                rep_a,
                rep_b,
            )
    # Zbar_i anticommutes with Xbar_i and commutes with Xbar_j, for every choice of
    # representative on either side.
    for i in (0, 1):
        for j in (0, 1):
            for z in Z_SUPPORTS[i]:
                for x in X_SUPPORTS[j]:
                    assert anticommute(z, x) == (i == j), (i, j, z, x)
    # Both stabilizers commute with every logical representative.
    for supports in (Z_SUPPORTS, X_SUPPORTS):
        for reps in supports.values():
            for rep in reps:
                assert not anticommute(rep, STABILIZER_SUPPORT), rep


def _check_frames():
    # Block 0 of the paper's placement, from Fig. 1b plus the orientation fixed by the
    # RZZ depth table: az to the right of the degree-3 vertex, d0 below it.
    block = LogicalBlock(0, {"d0": 16, "d1": 3, "d2": 2, "d3": 1, "ax": 0, "az": 4})

    assert block.physical("d1", frame=0) == 3
    assert block.physical("d1", frame=1) == 2
    assert block.physical("d2", frame=1) == 3
    assert block.physical("d0", frame=1) == 16, "frame must not move d0"
    assert block.role_at(4) == "az"
    assert block.role_at(99) is None

    # Zbar_0 has an adjacent-pair representative at frame 0; Zbar_1 does not, which is
    # why it needs the frame toggle.
    on_device = set(block.physical_edges())

    def adjacent(pair):
        return (min(pair), max(pair)) in on_device

    assert any(adjacent(s) for s in block.z_supports(0, frame=0))
    assert not any(adjacent(s) for s in block.z_supports(1, frame=0))
    assert any(adjacent(s) for s in block.z_supports(1, frame=1))

    # The intra-block ZZ is Zbar_0 Zbar_1 = Z_d1 Z_d2, an adjacent pair at frame 0.
    assert adjacent((block.physical("d1"), block.physical("d2")))


def _check_block_construction():
    block = LogicalBlock(0, {"d0": 16, "d1": 3, "d2": 2, "d3": 1, "ax": 0, "az": 4})
    assert block.physical_edges() == ((0, 1), (1, 2), (2, 3), (3, 4), (3, 16))
    assert block.site_to_physical() == {0: 16, 1: 3, 2: 4, 3: 2, 4: 1, 5: 0}
    assert block_from_sites(0, block.site_to_physical()) == block
    assert block.configured("syndrome") == {
        16: "d0",
        3: "az",
        4: "d1",
        2: "ax",
        1: "d2",
        0: "d3",
    }
    for bad, reason in [
        ({"d0": 0}, "incomplete"),
        ({"d0": 0, "d1": 0, "d2": 2, "d3": 3, "ax": 4, "az": 5}, "duplicate"),
    ]:
        try:
            LogicalBlock(1, bad)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for %s roles" % reason)


def self_test():
    _check_site_graph()
    _check_configurations()
    _check_operator_algebra()
    _check_frames()
    _check_block_construction()
    return True


if __name__ == "__main__":
    self_test()
    print("iceberg_block: all self-checks passed")
