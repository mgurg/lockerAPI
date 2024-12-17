"""create_languages_room_join_table

Revision ID: b04b40fb457a
Revises: 3a5692dd9dc8
Create Date: 2024-10-04 15:12:35.229276

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b04b40fb457a'
down_revision: Union[str, None] = '3a5692dd9dc8'
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
