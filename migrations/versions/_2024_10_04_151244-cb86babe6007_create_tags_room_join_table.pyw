"""create_tags_room_join_table

Revision ID: cb86babe6007
Revises: 3226268c9d81
Create Date: 2024-10-04 15:12:44.069354

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb86babe6007'
down_revision: Union[str, None] = '3226268c9d81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
