"""add_display_name_to_users

Revision ID: 84672722c881
Revises: c7f1a8e932b1
Create Date: 2026-09-19 10:26:11.259579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84672722c881'
down_revision: Union[str, Sequence[str], None] = 'c7f1a8e932b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('display_name', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'display_name')
