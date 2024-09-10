"""create cities table

Revision ID: b30a398b24e0
Revises: 
Create Date: 2024-09-09 15:47:49.414739

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b30a398b24e0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.create_table(
        "cities",
        sa.Column("id", sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("uuid", sa.VARCHAR(length=36), autoincrement=False, nullable=True),
        sa.Column("population", sa.VARCHAR(length=16), autoincrement=False, nullable=True),
        sa.Column("city", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("cities")
