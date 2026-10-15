from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import app
from backend.app.models.cafe import Cafe
from backend.app.models.category import Category
from backend.app.models.order import CafeTable, ConfirmationCode
from backend.app.models.product import Product

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    cafe = Cafe(name="کافه آرامش", slug="cafe-aramesh", is_active=True)
    db.add(cafe)
    db.flush()
    category = Category(cafe_id=cafe.id, name="قهوه", slug="coffee", sort_order=1, is_active=True)
    hidden_category = Category(cafe_id=cafe.id, name="مخفی", slug="hidden", sort_order=2, is_active=False)
    db.add_all([category, hidden_category])
    db.flush()
    db.add_all([
        Product(category_id=category.id, name="لاته", slug="latte", description="قهوه با شیر", price=Decimal("120000"), is_available=True, sort_order=1),
        Product(category_id=category.id, name="ناموجود", slug="unavailable", price=Decimal("90000"), is_available=False, sort_order=2),
        Product(category_id=hidden_category.id, name="محصول مخفی", slug="hidden-product", price=Decimal("50000"), is_available=True),
    ])
    db.add(CafeTable(cafe_id=cafe.id, table_number=7, qr_token="test-table-7"))
    db.commit()
    db.close()


def teardown_module():
    app.dependency_overrides.pop(get_db, None)


def test_cafe_details_returns_public_fields():
    response = client.get("/api/v1/cafes/1")
    assert response.status_code == 200
    assert response.json()["name"] == "کافه آرامش"


def test_menu_hides_inactive_categories_and_unavailable_products():
    response = client.get("/api/v1/cafes/1/menu")
    assert response.status_code == 200
    payload = response.json()
    assert [category["slug"] for category in payload["categories"]] == ["coffee"]
    assert [product["slug"] for product in payload["categories"][0]["products"]] == ["latte"]
    assert payload["categories"][0]["products"][0]["price"] == "120000"


def test_missing_cafe_returns_404():
    response = client.get("/api/v1/cafes/999/menu")
    assert response.status_code == 404


def test_categories_can_be_filtered_by_cafe():
    response = client.get("/api/v1/categories/?cafe_id=1")
    assert response.status_code == 200
    assert [item["slug"] for item in response.json()] == ["coffee"]


def test_products_can_be_filtered_by_category():
    response = client.get("/api/v1/products/?category_id=1")
    assert response.status_code == 200
    assert [item["slug"] for item in response.json()] == ["latte"]


def test_legacy_menu_shape_matches_existing_frontend():
    response = client.get("/api/cafes/1/menu")
    assert response.status_code == 200
    item = response.json()[0]
    assert item["cafe_id"] == 1
    assert item["active"] is True
    assert item["price"] == 120000


def test_end_to_end_order_code_approval_and_status():
    response = client.post("/api/orders", json={
        "table_number": 7,
        "items": [{"product_id": 1, "quantity": 2}],
    })
    assert response.status_code == 200
    order = response.json()
    assert len(order["confirmation_code"]) == 4
    assert order["total"] == 240000

    verified = client.post("/api/waiter/verify-code", json={"code": order["confirmation_code"]})
    assert verified.status_code == 200
    assert verified.json()["id"] == order["id"]

    approved = client.post(f"/api/waiter/orders/{order['id']}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "CONFIRMED"

    for next_status in ("PREPARING", "READY", "SERVED"):
        response = client.post(
            f"/api/waiter/orders/{order['id']}/status",
            json={"status": next_status},
        )
        assert response.status_code == 200
        assert response.json()["status"] == next_status


def test_invalid_quantity_is_rejected():
    response = client.post("/api/orders", json={
        "table_number": 7,
        "items": [{"product_id": 1, "quantity": 0}],
    })
    assert response.status_code == 422


def test_expired_code_is_rejected():
    response = client.post("/api/orders", json={
        "table_number": 7,
        "items": [{"product_id": 1, "quantity": 1}],
    })
    assert response.status_code == 200
    order = response.json()

    db = TestingSessionLocal()
    code = db.query(ConfirmationCode).filter_by(order_id=order["id"]).first()
    code.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db.commit()
    db.close()

    verify_response = client.post(
        "/api/waiter/verify-code",
        json={"code": order["confirmation_code"]},
    )
    assert verify_response.status_code == 410
