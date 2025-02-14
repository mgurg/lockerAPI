"""create companies table

Revision ID: 999c3d41ebdf
Revises: f974b6c2aa0e
Create Date: 2024-12-18 14:06:01.314836

"""
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '999c3d41ebdf'
down_revision: Union[str, None] = 'f974b6c2aa0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'companies',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False, default=uuid4),
        sa.Column('brand', sa.TEXT(), nullable=True),
        sa.Column('name', sa.TEXT(), nullable=False),
        sa.Column('gov_id', sa.TEXT(), nullable=True),
        sa.Column('gov_id_type', sa.TEXT(), nullable=True),
        sa.Column('website', sa.TEXT(), nullable=True),
        sa.Column('phone', sa.TEXT(), nullable=True),
        sa.Column('email', sa.TEXT(), nullable=True),
        sa.Column('notes', sa.TEXT(), nullable=True),
        sa.Column('location_id', sa.Integer(), nullable=False),
        # sa.Column('place_id', sa.TEXT(), nullable=True),
        sa.Column('verified_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.UniqueConstraint('gov_id', 'gov_id_type', name='uq_gov_id_and_type'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('companies')
