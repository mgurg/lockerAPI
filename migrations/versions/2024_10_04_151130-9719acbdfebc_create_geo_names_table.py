"""create_geo_names_table

Revision ID: 9719acbdfebc
Revises: c3b31d2c21fe
Create Date: 2024-10-04 15:11:30.930964

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9719acbdfebc'
down_revision: Union[str, None] = 'c3b31d2c21fe'
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
