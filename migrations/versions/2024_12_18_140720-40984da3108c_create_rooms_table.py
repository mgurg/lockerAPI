"""create rooms table

Revision ID: 40984da3108c
Revises: 80b9126a11c4
Create Date: 2024-12-18 14:07:20.960936

"""
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '40984da3108c'
down_revision: Union[str, None] = '80b9126a11c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'rooms',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False, default=uuid4),
        sa.Column('url_slug', sa.TEXT(), nullable=False),
        sa.Column('name', sa.TEXT(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('players_min', sa.Integer(), nullable=True),
        sa.Column('players_max', sa.Integer(), nullable=True),
        sa.Column('price_from', sa.DECIMAL(), nullable=True),
        sa.Column('currency', sa.TEXT(), nullable=True, default="PLN"),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('difficulty', sa.TEXT(), nullable=True),
        sa.Column('fear_level', sa.TEXT(), nullable=True),
        sa.Column('rating', sa.TEXT(), nullable=True),
        sa.Column('category', sa.TEXT(), nullable=True),
        sa.Column('booking_url', sa.TEXT(), nullable=True),
        sa.Column('url_yt', sa.TEXT(), nullable=True),
        sa.Column('notes', sa.TEXT(), nullable=True),
        sa.Column('hero_img', sa.TEXT(), nullable=True),
        sa.Column('icon_img', sa.TEXT(), nullable=True),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('lm_id', sa.TEXT(), nullable=True),
        sa.Column('mt_id', sa.TEXT(), nullable=True),
        sa.Column('sort_order', sa.TEXT(), nullable=True),
        sa.Column("verified_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("opened_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("suspended_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("closed_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('rooms')
