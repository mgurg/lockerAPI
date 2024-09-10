"""create cities table

Revision ID: b30a398b24e0
Revises: 
Create Date: 2024-09-09 15:47:49.414739

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b30a398b24e0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'locations',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('street_address', sa.String(255), nullable=False),
        sa.Column('city', sa.String(255), nullable=False),
        sa.Column('state_province', sa.String(255), nullable=True),
        sa.Column('postal_code', sa.String(255), nullable=True),
        sa.Column('country', sa.String(255), nullable=False),
        sa.Column('lat', sa.Numeric(10, 7), nullable=True),
        sa.Column('lng', sa.Numeric(10, 7), nullable=True)
    )


def downgrade():
    op.drop_table('locations')
