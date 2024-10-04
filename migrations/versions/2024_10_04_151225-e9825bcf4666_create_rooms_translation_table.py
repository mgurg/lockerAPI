"""create_rooms_translation_table

Revision ID: e9825bcf4666
Revises: 912c81548120
Create Date: 2024-10-04 15:12:25.218793

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e9825bcf4666'
down_revision: Union[str, None] = '912c81548120'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'room_translations',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('lang', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('lead', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_ai', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('room_translations')
