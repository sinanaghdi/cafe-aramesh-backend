"""Add tables and order confirmation workflow.

Revision ID: 0003_orders
Revises: 0002_dynamic_menu
Create Date: 2026-10-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_orders"
down_revision: Union[str, None] = "0002_dynamic_menu"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tables",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cafe_id", sa.Integer(), nullable=False),
        sa.Column("table_number", sa.Integer(), nullable=False),
        sa.Column("qr_token", sa.String(80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["cafe_id"], ["cafes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("cafe_id", "table_number", name="uq_tables_cafe_number"),
        sa.UniqueConstraint("qr_token"),
    )
    op.create_index("ix_tables_cafe_id", "tables", ["cafe_id"])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cafe_id", sa.Integer(), nullable=False),
        sa.Column("table_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="PENDING_WAITER"),
        sa.Column("subtotal", sa.Integer(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("notes", sa.String(500), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("served_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["cafe_id"], ["cafes.id"]),
        sa.ForeignKeyConstraint(["table_id"], ["tables.id"]),
    )
    op.create_index("ix_orders_cafe_id", "orders", ["cafe_id"])
    op.create_index("ix_orders_status", "orders", ["status"])

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Integer(), nullable=False),
        sa.Column("notes", sa.String(300), nullable=False, server_default=""),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])

    op.create_table(
        "confirmation_codes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(4), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_confirmation_codes_order_id", "confirmation_codes", ["order_id"])
    op.create_index("ix_confirmation_codes_code", "confirmation_codes", ["code"])


def downgrade() -> None:
    op.drop_index("ix_confirmation_codes_code", table_name="confirmation_codes")
    op.drop_index("ix_confirmation_codes_order_id", table_name="confirmation_codes")
    op.drop_table("confirmation_codes")
    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_table("order_items")
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_index("ix_orders_cafe_id", table_name="orders")
    op.drop_table("orders")
    op.drop_index("ix_tables_cafe_id", table_name="tables")
    op.drop_table("tables")
