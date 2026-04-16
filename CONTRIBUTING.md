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

1. Create a virtual environment and install the project with `pip install 'qc-grader[qiskit,jupyter] @ git+https://github.com/qiskit-community/Quantum-Challenge-Grader.git'` (or use `uv`)
  - You can install from a specific branch by adding `@your-branch-name` to the end.
2. Create an API token in https://quantum.cloud.ibm.com. The staging site will not work. The account must have at least one instance.
  - You will need this token in the future. Consider saving it with `QiskitRuntimeService.save_account()` with these [instructions](https://quantum.cloud.ibm.com/docs/en/guides/hello-world)
3. Launch a Python REPL inside the virtual environment with the environment variable `IBMCLOUD_API_KEY` set to your token.
  - If you previously used `QiskitRuntimeService.save_account()`, you can find your token in `~/.qiskit/qiskit-ibm.json`
4. In the REPL:

```python
>>> from qc_grader.challenges.test_challenge import submit_name, grade_ex1a
>>> submit_name("team_name")  # use this value
>>> grade_ex1a("")
```

To use a different grading server, set `QC_GRADER_URL` to `https://qac-grading-dev.quantum.ibm.com` or `http://127.0.0.1:5000`. 
