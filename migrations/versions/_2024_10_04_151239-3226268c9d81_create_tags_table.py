"""create_tags_table

Revision ID: 3226268c9d81
Revises: 33e07e1e529e
Create Date: 2024-10-04 15:12:39.259424

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '3226268c9d81'
down_revision: Union[str, None] = '33e07e1e529e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tags',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('name', sa.TEXT(), nullable=False),
        sa.Column('type', sa.TEXT(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
    )
    # Urodziny, Wieczór panieński


    op.bulk_insert(
        sa.table(
            'tags',
            sa.column('type', sa.TEXT()),
            sa.column('name', sa.TEXT()),
            sa.column('active', sa.Boolean()),
        ),
        [
            {'name': 'FROM_07_YEARS', 'type': "age_rating", 'active': True},
            {'name': 'FROM_12_YEARS', 'type': "age_rating", 'active': True},
            {'name': 'FROM_16_YEARS', 'type': "age_rating", 'active': True},
            {'name': 'FROM_18_YEARS', 'type': "age_rating", 'active': True},
            {'name': 'FOR_UNSUPERVISED_CHILDREN', 'type': "accessibility", 'active': True},
            {'name': 'FOR_SUPERVISED_CHILDREN', 'type': "accessibility", 'active': True},
            {'name': 'FOR_UNSUPERVISED_PET', 'type': "accessibility", 'active': True},
            {'name': 'FOR_SUPERVISED_PET', 'type': "accessibility", 'active': True},
            {'name': 'FOR_HANDICAPPED', 'type': "accessibility", 'active': True},
            {'name': 'NOT_FOR_HANDICAPPED', 'type': "accessibility", 'active': True},
            {'name': 'FOR_PREGNANT', 'type': "accessibility", 'active': True},
            {'name': 'NOT_FOR_PREGNANT', 'type': "accessibility", 'active': True},
            {'name': 'FOR_COMPANY_EVENTS', 'type': "accessibility", 'active': True},
            {'name': 'FOR_CHILDREN_EVENTS', 'type': "accessibility", 'active': True},
            {'name': 'WITH_ACTOR', 'type': "features", 'active': True},
            {'name': 'WITHOUT_ACTOR', 'type': "features", 'active': True},
        ]
    )


def downgrade() -> None:
    op.drop_table('tags')
