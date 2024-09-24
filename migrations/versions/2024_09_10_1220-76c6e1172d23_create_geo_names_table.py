"""create geo_names table

Revision ID: 76c6e1172d23
Revises: 03f47dbcd7f3
Create Date: 2024-09-10 12:20:52.722713

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76c6e1172d23'
down_revision: Union[str, None] = '03f47dbcd7f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'geo_names',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('city_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('name_ascii', sa.String(), nullable=False),
        sa.Column('country', sa.String(), nullable=False),
        sa.Column('lang', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ),
    )


def downgrade() -> None:
    op.drop_table('geo_names')
