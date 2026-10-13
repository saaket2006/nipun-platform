"""add_screening_tasks_table

Revision ID: 2d0cabfd21b5
Revises: 84672722c881
Create Date: 2026-10-13 22:42:04.395466

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d0cabfd21b5'
down_revision: Union[str, Sequence[str], None] = '84672722c881'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'screening_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recruiter_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=255), nullable=False),
        sa.Column('job_description', sa.Text(), nullable=False),
        sa.Column('resume_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ranked_results', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['recruiter_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_screening_tasks_id'), 'screening_tasks', ['id'], unique=False)
    op.create_index(op.f('ix_screening_tasks_recruiter_id'), 'screening_tasks', ['recruiter_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_screening_tasks_recruiter_id'), table_name='screening_tasks')
    op.drop_index(op.f('ix_screening_tasks_id'), table_name='screening_tasks')
    op.drop_table('screening_tasks')
