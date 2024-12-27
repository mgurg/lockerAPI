"""create geo_names table

Revision ID: f974b6c2aa0e
Revises: 932d037ca102
Create Date: 2024-12-18 14:04:13.481881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f974b6c2aa0e'
down_revision: Union[str, None] = '932d037ca102'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'geo_names',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('city_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.TEXT(), nullable=False),
        sa.Column('name_ascii', sa.TEXT(), nullable=False),
        sa.Column('country', sa.TEXT(), nullable=False),
        sa.Column('lang', sa.TEXT(), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ),
    )


def downgrade() -> None:
    op.drop_table('geo_names')
