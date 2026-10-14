"""Import model classes here so Alembic can discover their metadata."""

from backend.app.db.base import Base

__all__ = ["Base"]
