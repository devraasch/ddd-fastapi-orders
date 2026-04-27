# fastapi-ordering-ddd

Simple ordering system built with FastAPI, Clean Architecture, PostgreSQL, RabbitMQ and Docker.

## Overview

This project is a minimal MVP for order creation, designed to evolve with DDD concepts and event-driven architecture.

Current features:
- create orders
- health check endpoint
- PostgreSQL persistence (SQLAlchemy + **Alembic** migrations)
- RabbitMQ event publishing
- automated tests
- coverage support
- Docker-based local environment

## Architecture

The project follows a simplified Clean Architecture structure:

```text
app/
  domain/
  application/
  infrastructure/
  presentation/
alembic/
  env.py
  versions/
```

### Configuration: database URL

- **`app/infrastructure/config.py`**: `Settings` / `get_settings()` — `database_url` and `rabbitmq_url` (from `.env` / environment).
- **`app/infrastructure/database/base.py`**: `Base`, async `create_async_engine`, `async_session_maker` — runtime uses **`postgresql+asyncpg://`** (see `.env.example`).
- **Alembic** (`alembic/env.py`): same `DATABASE_URL` as the app; before opening a sync connection it rewrites **`postgresql+asyncpg://` → `postgresql+psycopg://`** so migrations use the existing psycopg driver. No second env var required for typical setups.

## Dependencies (uv)

```bash
uv sync --all-groups
```

## PostgreSQL (Docker)

Start only the database (and optionally RabbitMQ) if you are running the API on the host:

```bash
docker compose up -d db
# or full stack: docker compose up -d
```

Use a `DATABASE_URL` that matches your setup (see `.env`: host `db` from other Compose services, or `127.0.0.1` / `localhost` when the API runs on the host with published ports).

## Database migrations (Alembic)

Apply all pending migrations to the current database (creates/updates schema):

```bash
uv run alembic upgrade head
```

Check current revision / history:

```bash
uv run alembic current
uv run alembic history
```

**Initial migration** in this repo: `20260126_0001` — creates the `orders` table. The application **no longer** calls `Base.metadata.create_all()` at startup; schema changes are expected to go through Alembic.

### Create a new migration (after you change models)

1. Edit SQLAlchemy models under `app/infrastructure/database/`.
2. Autogenerate a revision (compare models to DB; review the file before committing):

   ```bash
   uv run alembic revision --autogenerate -m "describe_change"
   ```

3. Or add an empty revision and edit by hand:

   ```bash
   uv run alembic revision -m "describe_change"
   ```

4. Apply:

   ```bash
   uv run alembic upgrade head
   ```

## Run the API

```bash
uv run uvicorn app.main:app --reload
```

With Docker Compose (after DB is up and migrations applied for a fresh database):

```bash
docker compose up
```

For a new environment, run migrations **before** or **right after** Postgres is up, e.g.:

```bash
docker compose up -d db
uv run alembic upgrade head
docker compose up api
```

Or one-off in the API container (project mounted at `/app`):

```bash
docker compose run --rm api uv run alembic upgrade head
```

## Tests

```bash
uv run pytest
uv run pytest tests/unit
uv run pytest tests/integration
```

## Ruff

```bash
uv run ruff check app/ alembic/
```

## What changed at startup (vs `create_all`)

Previously the app created tables in `lifespan` with `Base.metadata.create_all()`. That is **removed**: the database schema is owned by **Alembic**. The FastAPI `lifespan` only wires the RabbitMQ publisher; Postgres is assumed to already be migrated.

---

Suggested commit message:

`chore(db): add Alembic migrations and remove create_all from app lifespan`
