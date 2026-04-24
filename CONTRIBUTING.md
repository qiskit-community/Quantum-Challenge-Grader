# Contributing

## Prerequisites

* [uv](https://docs.astral.sh/uv/getting-started/installation/)
* [Just](https://just.systems/man/en/)

## Installation

```sh
uv sync --all-extras
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
>>> from qc_grader.challenges.test_challenge import submit_name, grade_ex1a
>>> submit_name("team_name")  # use this value
>>> grade_ex1a("")
```

## Adding new labs

### Type validation

You must add the decorator `@typechecked` from `typeguard` to all lab exercises, along with precise type hints that describe the user's input. This decorator validates that the user gave the correct data type. For example:

```python
def grade_lab0_ex1(arg1: str, arg2: list[int], arg3: QuantumCircuit) -> None:
    ...
```

If the user needs to provide a dictionary with certain keys, use `typing.TypedDict`, rather than a more generic type hint like `dict` or `dict[str, int]`. `TypedDict` allows typeguard to validate that the user gave the correct dictionary format. For example:

```python
from typing import TypedDict

Ex1Input = TypedDict("Ex1Input", {"0": int, "1": int})

def grade_lab0_ex1(counts: Ex1Input) -> None:
    ...
```

It is often helpful to allow the user to provide a more flexible data type, and then to write some Python code to transform their input into a simpler format that the server will understand. When writing this type of transformation, think about how the user might make a mistake and consider adding validation, such as throwing a `ValueError` if they violate your assumptions. For example, this code is nice that it allows a user to either pass a `float` or an `ndarray`, which the code then transforms to `float` before sending to the server. This flexibility is useful because the challenge author knows that users will be working with NumPy for this exercise. Crucially, this example validates that their `ndarray` is a scalar:

```python
@typechecked
def grade_lab0_ex1(exp_val: np.ndarray | float) -> None:
    arr = np.asarray(exp_val)
    if arr.ndim != 0 and arr.size != 1:
        raise ValueError(
            f"exp_val must be a scalar, got shape {arr.shape}. "
            f"Use result[0].data.evs (not result.data.evs) for a single expectation value."
        )
    exp_val = float(arr.flat[0])
    grade(exp_val, "lab0-ex1", _CHALLENGE_ID)
```
