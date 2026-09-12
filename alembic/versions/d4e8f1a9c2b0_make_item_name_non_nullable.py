"""Make item name non-nullable.

Revision ID: d4e8f1a9c2b0
Revises: cfcf071a704d
Create Date: 2026-09-12 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d4e8f1a9c2b0"
down_revision: str | Sequence[str] | None = "cfcf071a704d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("items") as batch_op:
        batch_op.alter_column("name", existing_type=sa.String(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("items") as batch_op:
        batch_op.alter_column("name", existing_type=sa.String(), nullable=True)
