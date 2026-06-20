"""Initial migration

Revision ID: 8d24a8367f4d
Revises: 
Create Date: 2026-06-20 13:58:13.662594

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d24a8367f4d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'review_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('repo_name', sa.String(), nullable=False),
        sa.Column('pr_number', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('comments_posted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_review_logs_id'), 'review_logs', ['id'], unique=False)
    op.create_index(op.f('ix_review_logs_pr_number'), 'review_logs', ['pr_number'], unique=False)
    op.create_index(op.f('ix_review_logs_repo_name'), 'review_logs', ['repo_name'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_review_logs_repo_name'), table_name='review_logs')
    op.drop_index(op.f('ix_review_logs_pr_number'), table_name='review_logs')
    op.drop_index(op.f('ix_review_logs_id'), table_name='review_logs')
    op.drop_table('review_logs')
