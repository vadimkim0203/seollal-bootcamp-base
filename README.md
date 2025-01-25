# Seollal Bootcamp 2025 Backend

## Setup for Development

```shell
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
pre-commit install
```

## Formatting
```shell
ruff check --fix .
```

## Running

```shell
source .venv/bin/activate  # if not done already
docker compose up -d
alembic upgrade head
run
```

## Stopping

Ctrl + C, then

```shell
docker compose down
```
