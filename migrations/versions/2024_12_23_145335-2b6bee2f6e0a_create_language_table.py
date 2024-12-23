"""create language table

Revision ID: 2b6bee2f6e0a
Revises: 9ad8bdb91b11
Create Date: 2024-12-23 14:53:35.013425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2b6bee2f6e0a'
down_revision: Union[str, None] = '9ad8bdb91b11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'languages',
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column('name', sa.TEXT(), nullable=False),  # Translated name
        sa.Column('original_name', sa.TEXT(), nullable=False),  # Original spelling
        sa.Column('code', sa.TEXT(), nullable=False),  # Language code
        sa.PrimaryKeyConstraint('id')
    )
    op.bulk_insert(
        sa.table(
            'languages',
            sa.column('name', sa.TEXT()),
            sa.column('original_name', sa.TEXT()),
            sa.column('code', sa.TEXT()),
        ),
        [

            {'name': 'Polski', 'original_name': 'Polski', 'code': 'pl'},
            {'name': 'Angielski', 'original_name': 'English', 'code': 'en'},
            {'name': 'Niemiecki', 'original_name': 'Deutsch', 'code': 'de'},
            {'name': 'Hiszpański', 'original_name': 'Español', 'code': 'es'},
            {'name': 'Francuski', 'original_name': 'Français', 'code': 'fr'},
            {'name': 'Ukraiński', 'original_name': 'Українська', 'code': 'uk'},
            {'name': 'Czeski', 'original_name': 'Čeština', 'code': 'cs'},
            {'name': 'Słowacki', 'original_name': 'Slovenčina', 'code': 'sk'},
            {'name': 'Rosyjski', 'original_name': 'Русский', 'code': 'ru'},
        ]
    )


def downgrade() -> None:
    op.drop_table('languages')
