"""create locations table

Revision ID: 7c0abf870dc3
Revises: efaaa18ede1c
Create Date: 2024-12-18 14:01:14.714800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c0abf870dc3'
down_revision: Union[str, None] = 'efaaa18ede1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'locations',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('street_address', sa.TEXT(), nullable=False),
        sa.Column('city', sa.TEXT(), nullable=False),
        sa.Column('state_province', sa.TEXT(), nullable=True),
        sa.Column('postal_code', sa.TEXT(), nullable=True),
        sa.Column('country', sa.TEXT(), nullable=False),
        sa.Column('located_in', sa.TEXT(), nullable=True),  # mall center
        sa.Column('type', sa.TEXT(), nullable=False),  # Room / Department/ Company
        sa.Column('lat', sa.Numeric(10, 7), nullable=True, index=True),
        sa.Column('lon', sa.Numeric(10, 7), nullable=True, index=True)
    )


def downgrade() -> None:
    op.drop_table('locations')
