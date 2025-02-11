"""create locations table

Revision ID: 7c0abf870dc3
Revises: efaaa18ede1c
Create Date: 2024-12-18 14:01:14.714800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7c0abf870dc3'
down_revision: Union[str, None] = 'efaaa18ede1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'locations',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('street_address', sa.TEXT(), nullable=False),
        sa.Column('city', sa.TEXT(), nullable=False),
        sa.Column('state_province', sa.TEXT(), nullable=True),
        sa.Column('postal_code', sa.TEXT(), nullable=True),
        sa.Column('country', sa.TEXT(), nullable=False),
        sa.Column('located_in', sa.TEXT(), nullable=True),  # mall center
        sa.Column('type', sa.TEXT(), nullable=False),  # Room / Department/ Company
        sa.Column('lat', sa.Numeric(10, 7), nullable=True, index=True),
        sa.Column('lon', sa.Numeric(10, 7), nullable=True, index=True)
    )

    op.create_table(
        "entity_locations",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("entity_type", sa.TEXT(), nullable=False),
        sa.Column("entity_id", sa.Integer, nullable=False),
        sa.Column("location_id", sa.Integer, sa.ForeignKey("locations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("is_primary", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"),
                  onupdate=sa.text("now()")),
    )

    # Ensure entity_type can only have specific values
    op.execute(
        "ALTER TABLE entity_locations ADD CONSTRAINT chk_entity_type CHECK (entity_type IN ('company', 'department', 'room'))")

    # Add a composite index for efficient lookups
    op.create_index("idx_entity_type_entity_id", "entity_locations", ["entity_type", "entity_id"])


def downgrade() -> None:
    op.drop_table('locations')
    op.drop_index("idx_entity_type_entity_id", table_name="entity_locations")
    op.drop_table("entity_locations")
