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
