"""Vendored copy of the challenge's ``utils`` package, for the grading client.

``iceberg_device.py``, ``iceberg_block.py`` and ``iceberg_layout.py`` are **byte-identical
copies** of the challenge folder's ``utils/`` modules. They are vendored because the grading
functions have to build the toy lattice and placement to evaluate the participant's functions at
the fixed probes, and the installed ``qc-grader`` package has no access to the challenge folder:
importing ``utils`` worked only when the notebook happened to run with that folder as cwd, which
is not something the platform guarantees.

All three are stdlib-only. ``networkx`` is imported lazily inside the ``*_graph`` helpers, which
the probes never call, and is in any case already a ``qc-grader`` dependency.

**Keep these in step with the challenge's ``utils/``.** They are participant-facing: a
participant's function receives these classes and may call any of their methods, so a trimmed
re-implementation would diverge silently. ``lab_iceberg_test.py`` asserts the copies are
identical to the originals whenever it runs inside the challenge repo, which is what catches
drift; that check is skipped in a ``qc-grader`` checkout, where the originals do not exist.

Copies rather than a dependency because the challenge's ``utils`` is not a published package.
"""
