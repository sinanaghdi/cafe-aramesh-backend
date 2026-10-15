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
