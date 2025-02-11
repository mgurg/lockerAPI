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
        sa.Column("entity_type", sa.TEXT(), nullable=False),
        sa.Column('type', sa.TEXT(), nullable=False),
        sa.Column('value', sa.TEXT(), nullable=False),
        sa.Column('country_code', sa.TEXT(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),

        # Foreign keys
        # sa.Index("idx_contacts_entity", "entity_type", "entity_id")

    )


def downgrade() -> None:
    # Drop indexes
    # op.drop_index('idx_contacts_entity')

    # Drop table
    op.drop_table('contacts')
