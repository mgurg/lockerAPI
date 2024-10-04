"""create_companies_table

Revision ID: fc1e91dfc44a
Revises: 9719acbdfebc
Create Date: 2024-10-04 15:12:00.825081

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'fc1e91dfc44a'
down_revision: Union[str, None] = '9719acbdfebc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'companies',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('uuid', sa.UUID(), nullable=False),
        sa.Column('brand', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('street_address', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('state_province', sa.String(), nullable=True),
        sa.Column('postal_code', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=False),
        sa.Column('lat', sa.Numeric(10, 7), nullable=True),
        sa.Column('lng', sa.Numeric(10, 7), nullable=True)
    )


def downgrade() -> None:
    op.drop_table('companies')

