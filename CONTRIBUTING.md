# Contributing

## Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```sh
uv sync --all-extras
```

(uv automatically creates and manages a virtual environment.)

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
