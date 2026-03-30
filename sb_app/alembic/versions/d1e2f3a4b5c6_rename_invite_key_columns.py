"""rename invite_key table columns: ID->invite_id, key->code

Revision ID: d1e2f3a4b5c6
Revises: c3d5e7f9a1b2
Create Date: 2026-03-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, Sequence[str], None] = 'c3d5e7f9a1b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'invite_key', 'ID',
        new_column_name='invite_id',
        existing_type=sa.Integer(),
        existing_nullable=False
    )
    op.alter_column(
        'invite_key', 'key',
        new_column_name='code',
        existing_type=sa.String(9),
        existing_nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        'invite_key', 'code',
        new_column_name='key',
        existing_type=sa.String(9),
        existing_nullable=False
    )
    op.alter_column(
        'invite_key', 'invite_id',
        new_column_name='ID',
        existing_type=sa.Integer(),
        existing_nullable=False
    )
