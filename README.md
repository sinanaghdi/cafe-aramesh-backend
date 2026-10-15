# Cafe Aramesh Backend

FastAPI backend for the Cafe Aramesh digital menu, compatible with the existing frontend's legacy /api contract while also providing a versioned /api/v1 API.

## Stack

- Python 3.11+
- FastAPI + Uvicorn
- PostgreSQL + psycopg 3
- SQLAlchemy 2 + Alembic
- Pydantic Settings
- Pytest + HTTPX

## Windows setup

1. Install Python 3.11+ and PostgreSQL 15+.
2. From the repository root, create and activate a virtual environment:

   ~~~powershell
   py -3.11 -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ~~~

3. Copy .env.example to .env. Set DATABASE_URL to your PostgreSQL credentials. Never commit .env.
4. Create the PostgreSQL database named cafe_aramesh and a matching database role.
5. Apply all migrations:

   ~~~powershell
   alembic -c backend/alembic.ini upgrade head
   ~~~

6. To insert a small Persian demo menu and tables 1–8, run this explicitly:

   ~~~powershell
   python -m backend.app.seed
   ~~~

   Seeding is idempotent and does not run automatically when the API starts. It skips insertion if the cafe-aramesh slug already exists.
7. Start the API from the repository root:

   ~~~powershell
   uvicorn backend.app.main:app --reload
   ~~~

8. Open http://127.0.0.1:8000/docs. Liveness: /api/v1/health/live; database readiness: /api/v1/health/ready.

## Existing frontend compatibility (/api)

These routes retain the response shapes expected by the current Cafe Aramesh frontend.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/cafes/{cafe_id} | Cafe name and ID |
| GET | /api/cafes/{cafe_id}/menu | Flat list of available products |
| GET | /api/categories | Active categories |
| GET | /api/products | Available products |
| GET | /api/products/{product_id} | One available product |
| POST | /api/orders | Validate cart and create pending order with a four-digit code |
| GET | /api/orders/{order_id} | Read order details |
| GET | /api/orders/{order_id}/status | Read current status |
| POST | /api/waiter/login | Verify waiter PIN |
| GET | /api/waiter/orders | List orders for the waiter dashboard |
| POST | /api/waiter/verify-code | Verify a live confirmation code |
| POST | /api/waiter/orders/{order_id}/approve | Approve a pending order |
| POST | /api/waiter/orders/{order_id}/reject | Reject a pending order |
| POST | /api/waiter/orders/{order_id}/status | Advance status through preparation, ready, and served |

The order flow validates positive quantities, cafe/table/product association, product availability, prices from the database, confirmation-code expiry, and legal status transitions. Prices are integer toman amounts. A waiter PIN must be configured; an empty PIN rejects login.

**Security note:** waiter routes are kept compatible with the current frontend and still need a real authenticated session/role guard before production deployment. The current login response is a demo token, not a security credential. Change the example PIN before using a shared environment.

## Versioned menu API (/api/v1)

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/v1/cafes/{cafe_id} | Public cafe details |
| GET | /api/v1/cafes/{cafe_id}/menu | Cafe with active categories and available products |
| GET | /api/v1/categories/?cafe_id={cafe_id} | Active categories for one cafe |
| GET | /api/v1/products | Available products |
| GET | /api/v1/products/?category_id={category_id} | Available products in a category |
| GET | /api/v1/health/live | Process liveness |
| GET | /api/v1/health/ready | Database readiness |

Only active cafes/categories and available products appear in public menu responses. The versioned menu API is read-only; management endpoints should be added only with authentication and authorization.

## Tests

Run from the repository root:

~~~powershell
python -m pytest backend/tests -q
~~~

Tests use an isolated in-memory SQLite database and do not require a running PostgreSQL instance.

## Development rules

- Keep passwords, credentials, API keys, and .env out of source control.
- Apply schema changes through Alembic migrations; never call Base.metadata.create_all() at application startup.
- Validate request data with Pydantic.
- Keep routing, business logic, and database access separated.
- Run the test suite before integrating changes into the frontend.
