# Cafe Aramesh Backend

A clean FastAPI and PostgreSQL backend foundation for the Cafe Aramesh smart menu.

## Stack

- Python 3.11+
- FastAPI + Uvicorn
- PostgreSQL + psycopg 3
- SQLAlchemy 2
- Alembic migrations
- Pydantic Settings
- Pytest + HTTPX

## Current phase

**Phase 1 — Backend foundation:** application configuration, database session management, health endpoints, Alembic configuration, and starter tests. Domain features will be added in small, testable phases.

## Setup (Windows)

1. Install Python 3.11+ and PostgreSQL 15+.
2. Open a terminal at the repository root and create a virtual environment:

   ```powershell
   py -3.11 -m venv .venv
   .venv\\Scripts\\activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and update `DATABASE_URL` for your local PostgreSQL username, password, host, and database. Never commit `.env`.
4. Create the PostgreSQL database named `cafe_aramesh` and a role matching your connection settings.
5. Apply migrations:

   ```powershell
   alembic -c backend/alembic.ini upgrade head
   ```

6. Start the API from the repository root:

   ```powershell
   uvicorn backend.app.main:app --reload
   ```

7. Open `http://127.0.0.1:8000/docs`. Liveness: `/api/v1/health/live`; database readiness: `/api/v1/health/ready`.

## Tests

Run from the repository root:

```powershell
pytest backend/tests
```

The liveness test does not require PostgreSQL. The readiness test accepts either a successful connection or a clear `503` response when PostgreSQL is not running.

## Development rules

- Keep credentials and API keys out of source control.
- Make schema changes through Alembic migrations; do not use `Base.metadata.create_all()` during application startup.
- Validate API input/output with Pydantic schemas.
- Keep routing, business logic, and database access separated as features grow.
- Each feature should include tests before frontend integration.

## Planned feature order

1. Foundation, configuration, database session, and migrations.
2. Cafe profile, categories, and dynamic menu/products.
3. Customer cart validation and order creation.
4. Order confirmation code and waiter approval.
5. Order status and waiter/admin access control.
6. Frontend integration and end-to-end tests.
7. Smart combos and study/work mode.
