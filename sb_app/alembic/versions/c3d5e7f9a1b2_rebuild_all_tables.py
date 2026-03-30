"""rebuild all tables to match current ORM

Revision ID: c3d5e7f9a1b2
Revises: b7c4e9f20a31
Create Date: 2026-03-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c3d5e7f9a1b2'
down_revision: Union[str, Sequence[str], None] = 'b7c4e9f20a31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET FOREIGN_KEY_CHECKS = 0")

    op.execute("DROP TABLE IF EXISTS `transaction`")
    op.execute("DROP TABLE IF EXISTS `budget`")
    op.execute("DROP TABLE IF EXISTS `invite_key`")
    op.execute("DROP TABLE IF EXISTS `test`")
    op.execute("DROP TABLE IF EXISTS `user`")

    op.execute("SET FOREIGN_KEY_CHECKS = 1")

    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(24), nullable=False),
        sa.Column('create_date', sa.Date(), nullable=False),
        sa.Column('password_hash', sa.String(60), nullable=False),
        sa.Column('invite_code', sa.String(9), nullable=True),
        sa.Column('used_code', sa.Boolean(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'budget',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('budget_name', sa.String(25), nullable=False, server_default='overall'),
        sa.Column('budget_amount', sa.Numeric(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'budget_name')
    )

    op.create_table(
        'transaction',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('cost', sa.Numeric(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('budget_name', sa.String(25), nullable=True),
        sa.Column('account', sa.String(25), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['user_id', 'budget_name'],
            ['budget.user_id', 'budget.budget_name']
        ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'invite_key',
        sa.Column('ID', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('key', sa.String(9), nullable=False),
        sa.PrimaryKeyConstraint('ID')
    )

    op.create_table(
        'test',
        sa.Column('ID', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('Message', sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint('ID')
    )


def downgrade() -> None:
    pass
