"""Insert a small Persian demo menu after running Alembic migrations.

Run from the repository root:
    python -m backend.app.seed

This command is idempotent and never runs automatically on API startup.
"""
from sqlalchemy import select

from backend.app.db.session import SessionLocal
from backend.app.models.cafe import Cafe
from backend.app.models.category import Category
from backend.app.models.order import CafeTable
from backend.app.models.product import Product


DEMO_MENU = [
    ("نوشیدنی‌های گرم", "hot-drinks", [
        ("اسپرسو", "espresso", "قهوه اسپرسو", 70000),
        ("آمریکانو", "americano", "اسپرسو و آب داغ", 85000),
        ("لاته", "latte", "اسپرسو با شیر", 120000),
    ]),
    ("نوشیدنی‌های سرد", "cold-drinks", [
        ("آیس آمریکانو", "iced-americano", "آمریکانوی سرد", 95000),
        ("آیس لاته", "iced-latte", "لاته سرد", 135000),
    ]),
    ("کیک و دسر", "desserts", [
        ("چیزکیک", "cheesecake", "چیزکیک روز", 145000),
        ("براونی", "brownie", "براونی شکلاتی", 95000),
    ]),
]


def seed() -> None:
    with SessionLocal() as db:
        existing = db.scalar(select(Cafe.id).where(Cafe.slug == "cafe-aramesh"))
        if existing is not None:
            print("Demo cafe already exists; no changes made.")
            return

        cafe = Cafe(
            name="کافه آرامش",
            slug="cafe-aramesh",
            description="منوی دیجیتال کافه آرامش",
            is_active=True,
        )
        db.add(cafe)
        db.flush()

        for order, (name, slug, products) in enumerate(DEMO_MENU, start=1):
            category = Category(
                cafe_id=cafe.id,
                name=name,
                slug=slug,
                sort_order=order,
                is_active=True,
            )
            db.add(category)
            db.flush()
            for product_order, (product_name, product_slug, description, price) in enumerate(products, start=1):
                db.add(Product(
                    category_id=category.id,
                    name=product_name,
                    slug=product_slug,
                    description=description,
                    price=price,
                    is_available=True,
                    sort_order=product_order,
                ))

        for table_number in range(1, 9):
            db.add(CafeTable(
                cafe_id=cafe.id,
                table_number=table_number,
                qr_token=f"cafe-aramesh-table-{table_number}",
            ))

        db.commit()
        print("Demo cafe, menu, and tables 1–8 created.")


if __name__ == "__main__":
    seed()
