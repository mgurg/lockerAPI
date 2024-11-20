"""create_locations_table

Revision ID: 2dc5d7298080
Revises: 
Create Date: 2024-10-04 15:11:19.604905

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '2dc5d7298080'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'locations',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('street_address', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('state_province', sa.String(), nullable=True),
        sa.Column('postal_code', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=False),
        sa.Column('located_in', sa.String(), nullable=True), # mall center
        sa.Column('type', sa.String(), nullable=False), # Room / Department/ Company
        sa.Column('lat', sa.Numeric(10, 7), nullable=True),
        sa.Column('lon', sa.Numeric(10, 7), nullable=True)
    )


def downgrade():
    op.drop_table('locations')
