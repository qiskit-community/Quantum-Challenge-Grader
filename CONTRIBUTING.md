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
