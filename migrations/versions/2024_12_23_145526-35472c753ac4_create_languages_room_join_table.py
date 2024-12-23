"""create languages room join table

Revision ID: 35472c753ac4
Revises: 2b6bee2f6e0a
Create Date: 2024-12-23 14:55:26.682545

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35472c753ac4'
down_revision: Union[str, None] = '2b6bee2f6e0a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'room_language_link',
        sa.Column('room_id', sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column('language_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id']),
        sa.ForeignKeyConstraint(['language_id'], ['languages.id']),
        sa.PrimaryKeyConstraint("room_id", "language_id")
    )


def downgrade() -> None:
    op.drop_table('room_language_link')
