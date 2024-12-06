"""create_tags_table

Revision ID: 3226268c9d81
Revises: b04b40fb457a
Create Date: 2024-10-04 15:12:39.259424

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3226268c9d81'
down_revision: Union[str, None] = 'b04b40fb457a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
