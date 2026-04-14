fmt:
    uv run ruff format

lint:
    uv run ruff format --check
    uv run ruff check
    uv run ty check --error-on-warning

test:
    uv run pytest
