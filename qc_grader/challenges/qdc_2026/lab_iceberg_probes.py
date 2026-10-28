"""Probe inputs for the ``lab_iceberg`` grading functions.

The ORP exercises each consume the output of an earlier step, so the grading functions build
those intermediates themselves rather than trusting whatever the participant has in memory -
otherwise one mistake in 2.1 would be penalised again in every later exercise.

This is a reference implementation of the pipeline steps, used only to construct probe inputs.
It duplicates logic that also exists on the server by design: the client builds the inputs, the
server holds the answers, neither trusts the other's copy. Everything is seeded.

**Every public helper returns a fresh copy.** The results are handed straight to participant
code, which is free to sort, pop or append in place; the ``lru_cache`` underneath holds the
master. Returning the cached object itself let one exercise's function corrupt the probe for
every later exercise in the same kernel, which surfaces as a wrong answer rather than an error.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np

from .lab_iceberg import _orp_probe, _toy_system


def _parity_even(bits: str, num_logical_blocks: int) -> bool:
    """True when every block has even parity over its four data bits."""
    for b in range(num_logical_blocks):
        block_bits = [bits[-1 - (4 * b + k)] for k in range(4)]
        if sum(int(x) for x in block_bits) % 2 == 1:
            return False
    return True


@lru_cache(maxsize=4)
def _postselected(num_logical_blocks: int) -> tuple[list, list]:
    """The cached master. Call :func:`probe_postselected` instead."""
    data_list, syn_list = _orp_probe(num_logical_blocks)
    data, syn_rounds = data_list[0], syn_list[0]
    keep = [i for i, bits in enumerate(data) if _parity_even(bits, num_logical_blocks)]
    data_ps = [data[i] for i in keep]
    syn_ps = [[rnd[i] for i in keep] for rnd in syn_rounds]
    return data_ps, syn_ps


def probe_postselected(num_logical_blocks: int = 2) -> tuple[list, list]:
    """``(data_bitstrings_ps, syn_bitstrings_ps)`` of the first probe circuit.

    A fresh copy each call: the lists go to participant code, which may mutate them.
    """
    data_ps, syn_ps = _postselected(num_logical_blocks)
    return list(data_ps), [list(rnd) for rnd in syn_ps]


def probe_masks(syn_ps: list, num_logical_blocks: int = 2) -> dict:
    """``{detector: {"r", "mask", "n_ps"}}`` for the post-selected syndromes."""
    masks = {}
    for r, round_bits in enumerate(syn_ps):
        for v in range(2 * num_logical_blocks):
            fired = np.array([outcome[-1 - v] == "1" for outcome in round_bits])
            masks[v] = {"r": r, "mask": fired, "n_ps": int((~fired).sum())}
    return masks


@lru_cache(maxsize=4)
def _observables(num_logical_blocks: int) -> dict:
    """The cached master. Call :func:`probe_observables` instead."""
    from qiskit.quantum_info import SparsePauliOp

    from ._iceberg.iceberg_block import Z_SUPPORTS

    lattice, _, placement, _ = _toy_system()
    n_bits = 4 * len(placement.blocks)
    index = {b: i for i, b in enumerate(placement.blocks)}
    out = {}
    for site in lattice.nodes():
        b, lq = site  # the probe uses the identity site -> code-qubit map
        for rep, roles in enumerate(Z_SUPPORTS[lq]):
            bits = [4 * index[b] + int(role[1]) for role in roles]
            out[(site, rep)] = SparsePauliOp.from_sparse_list(
                [("ZZ", bits, 1.0)], num_qubits=n_bits
            )
    return out


def probe_observables(num_logical_blocks: int = 2) -> dict:
    """The reference ``encoded_obs`` for the toy system.

    A fresh dict each call. ``SparsePauliOp`` values are shared: Qiskit treats them as
    immutable and the probes only read them.
    """
    return dict(_observables(num_logical_blocks))


@lru_cache(maxsize=4)
def _correlations(num_logical_blocks: int) -> dict:
    """The cached master. Call :func:`probe_correlations` instead."""
    from qiskit.primitives import BitArray

    data_ps, syn_ps = probe_postselected(num_logical_blocks)
    masks = probe_masks(syn_ps, num_logical_blocks)
    enc = probe_observables(num_logical_blocks)
    corr = {key: np.zeros(len(masks)) for key in enc}
    arr = np.array(data_ps)
    for v, item in masks.items():
        mask = item["mask"]
        fired, quiet = arr[mask], arr[~mask]
        if len(fired) and len(quiet):
            ba1 = BitArray.from_samples(fired, num_bits=4 * num_logical_blocks)
            ba0 = BitArray.from_samples(quiet, num_bits=4 * num_logical_blocks)
            for key, obs in enc.items():
                corr[key][v] = abs(
                    float(ba1.expectation_values(obs))
                    - float(ba0.expectation_values(obs))
                )
    return corr


def probe_correlations(num_logical_blocks: int = 2) -> dict:
    """Reference ``Delta_j`` per observable, for the PART 2.5 probe.

    A fresh dict of fresh arrays each call: the values are mutable ndarrays.
    """
    return {key: arr.copy() for key, arr in _correlations(num_logical_blocks).items()}


def reference_obs_k() -> dict:
    """A hand-built ``obs_k`` with a known reference value and plateau, for 2.6.

    Deliberately discriminating: the three levels inside the [0.05, 0.5] window carry different
    O_k and different variances, so an inverse-variance weighted O_ref differs from a plain
    mean; and the longest plateau starts at k = 2 while the
    ``(O_k - O_ref)^2 + sig2_k`` fallback would pick k = 3, so skipping the plateau search is
    detected rather than silently accepted.
    """
    return {
        ("probe", 0): {
            "O_k": np.array([0.20, 0.35, 0.48, 0.50, 0.60, np.nan]),
            "f_k": np.array([1.00, 0.70, 0.45, 0.30, 0.15, 0.00]),
            "sig2_k": np.array([1e-4, 1e-4, 4e-4, 4e-4, 2.5e-3, np.nan]),
        }
    }
