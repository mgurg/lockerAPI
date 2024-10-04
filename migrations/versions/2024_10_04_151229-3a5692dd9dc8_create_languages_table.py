"""create_languages_table

Revision ID: 3a5692dd9dc8
Revises: e9825bcf4666
Create Date: 2024-10-04 15:12:29.038847

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a5692dd9dc8'
down_revision: Union[str, None] = 'e9825bcf4666'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'languages',
        sa.Column('id', sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=False)
    )


def downgrade() -> None:
    op.drop_table('languages')
