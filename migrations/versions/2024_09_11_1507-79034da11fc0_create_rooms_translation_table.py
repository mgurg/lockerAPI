"""create rooms_translation table

Revision ID: 79034da11fc0
Revises: ca1e37d10f89
Create Date: 2024-09-11 15:07:14.228760

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '79034da11fc0'
down_revision: Union[str, None] = 'ca1e37d10f89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'room_translations',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('lang', sa.String(length=2), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=False),
        sa.Column('lead', sa.String(length=512), nullable=True),
        sa.Column('description', sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('room_translations')
