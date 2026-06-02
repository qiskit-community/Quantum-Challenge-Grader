# Contributing

## Prerequisites

* [uv](https://docs.astral.sh/uv/getting-started/installation/)
* [Just](https://just.systems/man/en/)

## Installation

```sh
uv sync
```

(uv automatically creates and manages a virtual environment.)

## Format code

```
just fmt
```

## Lint

```
just lint
```

To run the individual linters:

* Ruff: `uv run ruff check`
* Ty (type check): `uv run ty check`

## Tests

```
just test
```

## Update dependencies

([Original documentation](https://docs.astral.sh/uv/concepts/projects/dependencies/))

Add a core dependency:

```
uv add <dependency>
```

Add an extra:

```
uv add <dependnecy> --optional qiskit
```

Add a dev dependency:

```
uv add <dependency> --dev
```

## Run the client

Use this workflow to test the Python client against the Grader server.

### Initial setup

You must create a Quantum API token for an account with at least one instance.

Prod server:

1. Use https://quantum.cloud.ibm.com to create the API key
2. Save the key by running `uv run python`, then this code:

```python
from qiskit_ibm_runtime import QiskitRuntimeService

QiskitRuntimeService.save_account(
    token="<your-api-key>",
    instance="<CRN>",
)
```
3. Close the REPL.

Staging or local development server:

1. Use https://quantum.test.cloud.ibm.com to create the API key.
2. Save the key by running `uv run python`, then this code:

```python
from qiskit_ibm_runtime import QiskitRuntimeService

QiskitRuntimeService.save_account(
    token="<your-api-key>",
    instance="<CRN>",
    name="grader-staging",
)
```
3. Close the REPL.

### How to run

1. Launch a Python REPL:
  - Prod server: `uv run python`
  - Staging server: `STAGING=1 uv run python`
  - Local development server: `DEV=1 uv run python`
2. In the REPL, import and run your exercises. For example:

```python
>>> from qc_grader.challenges.qgss_2026 import grade_lab0_ex1
>>> grade_lab0_ex1()
```

For developers testing how the server behaves, you can use the files from `qc_grader.challenges.test_challenges`, such as `grade_success` from `qc_grader.challenges.test_challenges.individual`.

## Adding new labs

A *lab* is a single Python file corresponding to a Jupyter notebook that users receive. Each *challenge* has one or more labs. When you add new exercises to the server, add a matching Python file here so that users can call grading functions from their Jupyter notebooks.

Create `qc_grader/challenges/{challenge}/{lab}.py`, e.g. `qc_grader/challenges/qgss_2027/lab1.py`.

The `_CHALLENGE` and `_LAB` constants, and each exercise string (e.g., `"ex1"`), must exactly match the identifiers configured on the server. These are permanent: once a challenge is live, changing them breaks existing notebook submissions.

A minimal lab file:

```python
# qc_grader/challenges/qgss_2027/lab1.py
from typing import Any

from typeguard import typechecked

from qc_grader.grader.grade import grade_answer

_CHALLENGE = "qgss_2027"
_LAB = "lab1"


def _grade(answer: Any, exercise: str) -> None:
    grade_answer(answer, lab=_LAB, exercise=exercise, challenge=_CHALLENGE)


@typechecked
def grade_lab1_ex1(answer: str) -> None:
    _grade(answer, "ex1")


@typechecked
def grade_lab1_ex2(answer: int) -> None:
    _grade(answer, "ex2")
```

Then, export every grading function from the challenge package's `__init__.py`:

```python
# qc_grader/challenges/qgss_2027/__init__.py
from .lab1 import grade_lab1_ex1, grade_lab1_ex2

__all__ = ["grade_lab1_ex1", "grade_lab1_ex2"]
```

Users can then import your functions like this:

```python
from qc_grader.challenges.qgss_2027 import grade_lab1_ex1
```

### Type validation

All grading functions must use the `@typechecked` decorator from `typeguard` and precise type hints on the answer parameter. This lets the client reject submissions with the wrong data type before they reach the server.

Use the most specific type that describes what the user should submit — `QuantumCircuit`, `Statevector`, `int`, `float`, etc. Avoid `Any` or bare `dict` and bare `list`.

```python
from typeguard import typechecked

@typechecked
def grade_lab1_ex1(arg1: str, arg2: list[int], arg3: QuantumCircuit) -> None:
    ...
```

#### Dictionaries with required keys

If the user submits a dictionary with specific keys, use `typing.TypedDict` rather than a generic `dict`. `TypedDict` allows `typechecked` to validate each key's name and type:

```python
from typing import TypedDict

from typeguard import typechecked

Ex1Input = TypedDict("Ex1Input", {"0": int, "1": int})

@typechecked
def grade_lab0_ex1(counts: Ex1Input) -> None:
    ...
```

#### Multiple accepted types

Use a union (`|`) to accept more than one type:

```python
@typechecked
def grade_lab0_ex1(answer: int | float) -> None:
    ...
```

#### Flexible types with transformation

It is often helpful to accept a more flexible data type and transform it before sending to the server. When doing so, anticipate likely user mistakes and raise a `ValueError` if they violate your assumptions. For example, this accepts either a `float` or an `ndarray` (useful when users are working with NumPy) and validates that the array is a scalar:

```python
from typeguard import typechecked

@typechecked
def grade_lab0_ex1(exp_val: np.ndarray | float) -> None:
    arr = np.asarray(exp_val)
    if arr.ndim != 0 and arr.size != 1:
        raise ValueError(
            f"exp_val must be a scalar, got shape {arr.shape}. "
            f"Use result[0].data.evs (not result.data.evs) for a single expectation value."
        )
    exp_val = float(arr.flat[0])
    _grade(exp_val, "ex1")
```
