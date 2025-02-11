"""create departments table

Revision ID: 80b9126a11c4
Revises: 999c3d41ebdf
Create Date: 2024-12-18 14:06:52.872413

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80b9126a11c4'
down_revision: Union[str, None] = '999c3d41ebdf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'departments',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('uuid', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.TEXT(), nullable=False),


        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('departments')

