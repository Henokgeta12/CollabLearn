"""add group tasks group notes

Revision ID: 33b2a0bfc9de
Revises: 23644d9fe089
Create Date: 2024-09-02 13:48:22.203050

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '33b2a0bfc9de'
down_revision = '23644d9fe089'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('group_notes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('last_updated_by', sa.Integer(), nullable=True),
    sa.Column('last_updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['study_groups.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['last_updated_by'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('group_notes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_group_notes_group_id'), ['group_id'], unique=False)

    op.create_table('group_tasks',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('task_description', sa.Text(), nullable=False),
    sa.Column('assigned_to', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=15), nullable=False),
    sa.Column('due_date', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['group_id'], ['study_groups.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('group_tasks', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_group_tasks_assigned_to'), ['assigned_to'], unique=False)
        batch_op.create_index(batch_op.f('ix_group_tasks_group_id'), ['group_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group_tasks', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_group_tasks_group_id'))
        batch_op.drop_index(batch_op.f('ix_group_tasks_assigned_to'))

    op.drop_table('group_tasks')
    with op.batch_alter_table('group_notes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_group_notes_group_id'))

    op.drop_table('group_notes')
    # ### end Alembic commands ###
