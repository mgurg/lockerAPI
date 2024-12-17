"""create_cities_table

Revision ID: c3b31d2c21fe
Revises: 2dc5d7298080
Create Date: 2024-10-04 15:11:26.616469

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c3b31d2c21fe'
down_revision: Union[str, None] = '2dc5d7298080'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'cities',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        # sa.Column('local_id', sa.TEXT(), nullable=True),
        # sa.Column('local_id_type', sa.TEXT(), nullable=True),
        sa.Column('lat', sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column('lon', sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column('lat_min', sa.Numeric(precision=10, scale=7), nullable=True),  # South Latitude
        sa.Column('lat_max', sa.Numeric(precision=10, scale=7), nullable=True),  # North Latitude
        sa.Column('lon_min', sa.Numeric(precision=10, scale=7), nullable=True),  # West Longitude
        sa.Column('lon_max', sa.Numeric(precision=10, scale=7), nullable=True),  # East Longitude
        sa.Column('population', sa.Integer(), nullable=True),
        sa.Column('importance', sa.Float(), nullable=True),
        sa.Column('category', sa.TEXT(), nullable=False),
        sa.Column('region', sa.TEXT(), nullable=True),
        sa.Column('country', sa.TEXT(), nullable=True),
        sa.Column('seo_title', sa.TEXT(), nullable=True),
        sa.Column('seo_description', sa.TEXT(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('cities')
