"""create locations table

Revision ID: 7c0abf870dc3
Revises: efaaa18ede1c
Create Date: 2024-12-18 14:01:14.714800

"""
from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7c0abf870dc3'
down_revision: Union[str, None] = 'efaaa18ede1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'locations',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False, default=uuid4, server_default=sa.text("gen_random_uuid()")),
        sa.Column('street_name', sa.TEXT(), nullable=True),
        sa.Column('street_number', sa.TEXT(), nullable=True),
        sa.Column('city', sa.TEXT(), nullable=False),
        sa.Column('state_province', sa.TEXT(), nullable=True),
        sa.Column('postal_code', sa.TEXT(), nullable=True),
        sa.Column('country', sa.TEXT(), nullable=False),
        sa.Column('located_in', sa.TEXT(), nullable=True),  # mall center
        sa.Column('type', sa.TEXT(), nullable=False), # room / department
        sa.Column('lat', sa.Numeric(10, 7), nullable=True, index=True),
        sa.Column('lon', sa.Numeric(10, 7), nullable=True, index=True)
    )

    # op.create_table(
    #     'entity_locations',
    #     sa.Column('id', sa.Integer(), primary_key=True),
    #     sa.Column('location_id', sa.Integer(), nullable=False),
    #     sa.Column('entity_id', sa.Integer(), nullable=False),
    #     sa.Column('entity_type', sa.TEXT(), nullable=False),
    #
    #     # Foreign key
    #     sa.ForeignKeyConstraint(['location_id'], ['locations.id'],
    #                             name='fk_entity_location_location_id',
    #                             ondelete='CASCADE'
    #                             ),
    #
    #     # Unique constraint
    #     sa.UniqueConstraint('entity_id', 'entity_type', 'location_id', name='uq_entity_location'),
    #
    #     # Check constraint for entity_type
    #     sa.CheckConstraint("entity_type IN ('company', 'department')", name='ck_entity_type_values')
    # )


def downgrade() -> None:
    # op.drop_table("entity_locations")
    op.drop_table('locations')
