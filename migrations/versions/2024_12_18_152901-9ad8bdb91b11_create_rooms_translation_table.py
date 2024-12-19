"""create rooms translation table

Revision ID: 9ad8bdb91b11
Revises: 40984da3108c
Create Date: 2024-12-18 15:29:01.259841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ad8bdb91b11'
down_revision: Union[str, None] = '40984da3108c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'room_translations',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('lang', sa.TEXT(), nullable=False),
        sa.Column('title', sa.TEXT(), nullable=False),
        sa.Column('lead', sa.TEXT(), nullable=True),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('is_ai', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('room_translations')
