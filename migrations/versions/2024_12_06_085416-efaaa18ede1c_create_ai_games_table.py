"""create ai_games table

Revision ID: efaaa18ede1c
Revises: 
Create Date: 2024-12-06 08:54:16.340060

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'efaaa18ede1c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ai_games',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('uuid', sa.UUID(), nullable=False),
        sa.Column('theme', sa.TEXT(), nullable=False),
        sa.Column('description', sa.TEXT(), nullable=False),
        sa.Column('difficulty', sa.TEXT(), nullable=False),
        sa.Column('category', sa.TEXT(), nullable=False),
        sa.Column('occasion', sa.TEXT(), nullable=False),
        sa.Column('email', sa.TEXT(), nullable=True),
        sa.Column('ip', sa.TEXT(), nullable=True),
        sa.Column('location', sa.TEXT(), nullable=True),
        sa.Column('is_valid', sa.Boolean(), nullable=True),
        sa.Column('token', sa.TEXT(), nullable=False),
        sa.Column('intro', sa.TEXT(), nullable=False),
        sa.Column('ending', sa.TEXT()),
        sa.Column('puzzle_1', sa.TEXT()),
        sa.Column('puzzle_2', sa.TEXT()),
        sa.Column('puzzle_3', sa.TEXT()),
        sa.Column('puzzle_4', sa.TEXT()),
        sa.Column('state', sa.TEXT(), nullable=False),
        sa.Column('current_puzzle', sa.Integer(), nullable=False),
        sa.Column('hints_remaining', sa.Integer(), nullable=False),
        sa.Column('wrong_answers', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('remarks', sa.TEXT()),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index('idx_uuid', 'ai_games', ['uuid'])


def downgrade() -> None:
    op.drop_table('ai_games')
