"""create_departments_table

Revision ID: 16147e63828f
Revises: fc1e91dfc44a
Create Date: 2024-10-04 15:12:04.753304

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '16147e63828f'
down_revision: Union[str, None] = 'fc1e91dfc44a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'departments',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('uuid', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('location_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.TEXT(), nullable=False),


        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('departments')

