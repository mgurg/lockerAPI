"""create contacts table

Revision ID: 33e07e1e529e
Revises: 35472c753ac4
Create Date: 2025-02-07 20:20:52.052774

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from uuid import uuid4


# revision identifiers, used by Alembic.
revision: str = '33e07e1e529e'
down_revision: Union[str, None] = '35472c753ac4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create contacts table
    op.create_table(
        'contacts',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False, default=uuid4),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.TEXT(), nullable=False),
        sa.Column('value', sa.TEXT(), nullable=False),
        sa.Column('country_code', sa.TEXT(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    )

    # Create department_contacts association table
    op.create_table(
        'contacts_departments',
        sa.Column('department_id', sa.INTEGER(), sa.ForeignKey('departments.id', ), nullable=False),
        sa.Column('contact_id', sa.INTEGER(), sa.ForeignKey('contacts.id', ), nullable=False),
        sa.PrimaryKeyConstraint('department_id', 'contact_id'),
    )


def downgrade() -> None:
    # Drop table
    op.drop_table('contacts_departments')
    op.drop_table('contacts')
