"""create rooms table

Revision ID: ca1e37d10f89
Revises: 76c6e1172d23
Create Date: 2024-09-10 12:21:17.712885

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ca1e37d10f89'
down_revision: Union[str, None] = '76c6e1172d23'
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
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('rooms')
