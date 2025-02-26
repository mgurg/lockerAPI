"""create cities table

Revision ID: 932d037ca102
Revises: 7c0abf870dc3
Create Date: 2024-12-18 14:03:32.641446

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '932d037ca102'
down_revision: Union[str, None] = '7c0abf870dc3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'cities',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('name', sa.TEXT(), nullable=False),
        sa.Column('name_ascii', sa.TEXT(), nullable=False),
        sa.Column('lat', sa.Numeric(precision=10, scale=7), nullable=True, index=True),
        sa.Column('lon', sa.Numeric(precision=10, scale=7), nullable=True, index=True),
        sa.Column('lat_min', sa.Numeric(precision=10, scale=7), nullable=True),  # South Latitude
        sa.Column('lat_max', sa.Numeric(precision=10, scale=7), nullable=True),  # North Latitude
        sa.Column('lon_min', sa.Numeric(precision=10, scale=7), nullable=True),  # West Longitude
        sa.Column('lon_max', sa.Numeric(precision=10, scale=7), nullable=True),  # East Longitude
        sa.Column('population', sa.Integer(), nullable=True),
        sa.Column('importance', sa.Float(), nullable=True),
        sa.Column('category', sa.TEXT(), nullable=False),
        sa.Column('region', sa.TEXT(), nullable=True),
        sa.Column('country', sa.TEXT(), nullable=True),
        sa.Column('language', sa.TEXT(), nullable=True),
        sa.Column('seo_title', sa.TEXT(), nullable=True),
        sa.Column('seo_description', sa.TEXT(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('cities')
