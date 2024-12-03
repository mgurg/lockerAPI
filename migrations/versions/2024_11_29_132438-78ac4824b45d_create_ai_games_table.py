"""create ai_games table

Revision ID: 78ac4824b45d
Revises: cb86babe6007
Create Date: 2024-11-29 13:24:38.980839

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '78ac4824b45d'
down_revision: Union[str, None] = 'cb86babe6007'
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
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('ai_games')
