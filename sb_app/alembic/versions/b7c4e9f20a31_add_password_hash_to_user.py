"""add password_hash to user

Revision ID: b7c4e9f20a31
Revises: 34ea8ec03198
Create Date: 2026-03-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'b7c4e9f20a31'
down_revision: Union[str, Sequence[str], None] = '34ea8ec03198'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Truncate user data and add password_hash column."""
    # Disable FK checks so dependent tables can be truncated first
    op.execute("SET FOREIGN_KEY_CHECKS = 0")
    op.execute("TRUNCATE TABLE transaction")
    op.execute("TRUNCATE TABLE budget")
    op.execute("TRUNCATE TABLE user")
    op.execute("SET FOREIGN_KEY_CHECKS = 1")

    op.add_column(
        'user',
        sa.Column('password_hash', mysql.CHAR(60), nullable=False)
    )


def downgrade() -> None:
    """Remove password_hash column."""
    op.drop_column('user', 'password_hash')
