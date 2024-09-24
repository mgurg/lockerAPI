"""create languages_room join table

Revision ID: e9b39fccc92a
Revises: bc3907794df7
Create Date: 2024-09-12 11:28:04.252464

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e9b39fccc92a'
down_revision: Union[str, None] = 'bc3907794df7'
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
    op.drop_table('room_language')
