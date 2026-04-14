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
