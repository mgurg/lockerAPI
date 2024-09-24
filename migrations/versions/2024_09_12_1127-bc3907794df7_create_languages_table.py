"""create languages table

Revision ID: bc3907794df7
Revises: 79034da11fc0
Create Date: 2024-09-12 11:27:49.754919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc3907794df7'
down_revision: Union[str, None] = '79034da11fc0'
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
