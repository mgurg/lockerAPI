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

    # Create index on 'city_id'
    op.create_index('ix_geo_names_city_id', 'geo_names', ['city_id'])

    # Create index on 'country'
    op.create_index('ix_geo_names_country', 'geo_names', ['country'])

    # Create index on 'name_ascii'
    op.create_index('ix_geo_names_name_ascii', 'geo_names', ['name_ascii'])

    # Create composite index on 'country', 'name_ascii', and 'lang'
    op.create_index('ix_geo_names_country_name_ascii_lang', 'geo_names', ['country', 'name_ascii', 'lang'])



def downgrade() -> None:
    # Remove indexes
    op.drop_index('ix_geo_names_city_id', table_name='geo_names')
    op.drop_index('ix_geo_names_country', table_name='geo_names')
    op.drop_index('ix_geo_names_name_ascii', table_name='geo_names')
    op.drop_index('ix_geo_names_country_name_ascii_lang', table_name='geo_names')

    op.drop_table('geo_names')
