"""create_tags_table

Revision ID: 3226268c9d81
Revises: 33e07e1e529e
Create Date: 2024-10-04 15:12:39.259424

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3226268c9d81'
down_revision: Union[str, None] = '33e07e1e529e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tags',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('name', sa.TEXT(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table('languages')
