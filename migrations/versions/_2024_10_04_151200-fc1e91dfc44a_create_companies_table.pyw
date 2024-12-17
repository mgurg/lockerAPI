"""create_companies_table

Revision ID: fc1e91dfc44a
Revises: 9719acbdfebc
Create Date: 2024-10-04 15:12:00.825081

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

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
        sa.Column('brand', sa.TEXT(), nullable=True),
        sa.Column('name', sa.TEXT(), nullable=False),
        sa.Column('gov_id', sa.TEXT(), nullable=True),
        sa.Column('gov_id_type', sa.TEXT(), nullable=True),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('website', sa.TEXT(), nullable=True),
        sa.Column('place_id', sa.TEXT(), nullable=True),
        sa.Column('phone', sa.TEXT(), nullable=True),
        sa.Column('email', sa.TEXT(), nullable=True),
        sa.Column('verified_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.UniqueConstraint('gov_id', 'gov_id_type', name='uq_gov_id_and_type'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('companies')
