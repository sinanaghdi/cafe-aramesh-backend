# Cafe Aramesh Backend

A FastAPI and PostgreSQL backend for the Cafe Aramesh smart menu.

## Stack

- Python 3.11+
- FastAPI + Uvicorn
- PostgreSQL + psycopg 3
- SQLAlchemy 2
- Alembic migrations
- Pydantic Settings
- Pytest + HTTPX

## Current phase

**Phase 2 — Dynamic menu read API:** SQLAlchemy models and a database migration for cafes, categories, and products, plus read-only endpoints for public cafe/menu data. No real cafe data is seeded automatically; an empty database returns an empty product/category list for an existing cafe, and a 404 for a missing/inactive cafe.

## Setup (Windows)

1. Install Python 3.11+ and PostgreSQL 15+.
2. Open a terminal at the repository root and create a virtual environment:

   ```powershell
   py -3.11 -m venv .venv
   .venv\Scripts\activate
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

## Dynamic menu endpoints

All routes use the `/api/v1` prefix.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/cafes/{cafe_id}` | Public cafe details |
| GET | `/cafes/{cafe_id}/menu` | Cafe details plus active categories and available products |
| GET | `/categories/?cafe_id={cafe_id}` | Active categories for one cafe |
| GET | `/products/` | Available products across active categories |
| GET | `/products/?category_id={category_id}` | Available products in one category |

Example menu request: `GET /api/v1/cafes/1/menu`.

Only active cafes/categories and available products appear in public menu responses. Prices are integer toman amounts. These endpoints are read-only; protected management endpoints will be added after authentication and authorization are designed.

## Tests

Run from the repository root:

```powershell
python -m pytest backend/tests -q
```

Menu tests use an isolated in-memory SQLite database and do not require PostgreSQL. The readiness test accepts either a successful database connection or a clear `503` response when PostgreSQL is not running.

## Development rules

- Keep credentials and API keys out of source control.
- Make schema changes through Alembic migrations; do not use `Base.metadata.create_all()` during application startup.
- Validate API input/output with Pydantic schemas.
- Keep routing, business logic, and database access separated.
- Include tests for each feature before frontend integration.

## Feature roadmap

1. Foundation, configuration, database session, and migrations.
2. Cafe profile, categories, and dynamic menu/products. **In progress on this branch.**
3. Customer cart validation and order creation.
4. Order confirmation code and waiter approval.
5. Order status and waiter/admin access control.
6. Frontend integration and end-to-end tests.
7. Smart combos and study/work mode.
