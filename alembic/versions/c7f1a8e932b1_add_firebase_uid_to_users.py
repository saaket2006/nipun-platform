"""add_firebase_uid_to_users

Revision ID: c7f1a8e932b1
Revises: b4f8c92d1e5a
Create Date: 2026-09-15 15:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7f1a8e932b1'
down_revision: Union[str, Sequence[str], None] = 'b4f8c92d1e5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add firebase_uid to users table (nullable initially for clean migration)
    op.add_column('users', sa.Column('firebase_uid', sa.String(length=128), nullable=True))
    op.create_index(op.f('ix_users_firebase_uid'), 'users', ['firebase_uid'], unique=True)
    
    # Make hashed_password nullable for users authenticated purely through Firebase
    op.alter_column('users', 'hashed_password', existing_type=sa.String(length=255), nullable=True)


def downgrade() -> None:
    op.alter_column('users', 'hashed_password', existing_type=sa.String(length=255), nullable=False)
    op.drop_index(op.f('ix_users_firebase_uid'), table_name='users')
    op.drop_column('users', 'firebase_uid')
