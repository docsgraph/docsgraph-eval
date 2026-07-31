# Contributing to docsgraph-eval

## Setup

```bash
uv sync --all-extras --locked
uv run pre-commit install
```

## Before opening a PR

Run the full check suite and make sure it is clean:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```

`pre-commit` runs the linting and type-checking hooks automatically on
commit once installed; running the commands above manually is still a good
way to catch test failures before pushing.

## Shared guidelines

For organization-wide conventions (issue/PR etiquette, code of conduct,
security policy), see [docsgraph/.github](https://github.com/docsgraph/.github).
