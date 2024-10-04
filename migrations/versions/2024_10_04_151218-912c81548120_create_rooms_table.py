"""create_rooms_table

Revision ID: 912c81548120
Revises: 16147e63828f
Create Date: 2024-10-04 15:12:18.269921

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '912c81548120'
down_revision: Union[str, None] = '16147e63828f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'rooms',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('uuid', sa.UUID(), nullable=False),
        sa.Column('url_slug', sa.String(), nullable=False),
        # sa.Column('city_id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('players_min', sa.Integer(), nullable=True),
        sa.Column('players_max', sa.Integer(), nullable=True),
        sa.Column('price_from', sa.DECIMAL(), nullable=True),
        sa.Column('game_duration', sa.Integer(), nullable=True),
        sa.Column('game_difficulty', sa.String(), nullable=True),
        sa.Column('game_fear_index', sa.String(), nullable=True),
        sa.Column('reservation_url', sa.String(), nullable=True),
        sa.Column('url_yt', sa.String(), nullable=True),
        sa.Column('lm_id', sa.String(), nullable=True),
        sa.Column('mt_id', sa.String(), nullable=True),
        sa.Column('order', sa.String(), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        # sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('rooms')
