"""Initialize migration history before domain tables are introduced.

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-14
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the Alembic version table; domain tables arrive in later revisions."""
    pass


def downgrade() -> None:
    """No domain tables are created by this baseline revision."""
    pass
