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
        sa.Column('street_address', sa.TEXT(), nullable=False),
        sa.Column('city', sa.TEXT(), nullable=False),
        sa.Column('state_province', sa.TEXT(), nullable=True),
        sa.Column('postal_code', sa.TEXT(), nullable=True),
        sa.Column('country', sa.TEXT(), nullable=False),
        sa.Column('located_in', sa.TEXT(), nullable=True), # mall center
        sa.Column('type', sa.TEXT(), nullable=False), # Room / Department/ Company
        sa.Column('lat', sa.Numeric(10, 7), nullable=True),
        sa.Column('lon', sa.Numeric(10, 7), nullable=True)
    )


def downgrade():
    op.drop_table('locations')
