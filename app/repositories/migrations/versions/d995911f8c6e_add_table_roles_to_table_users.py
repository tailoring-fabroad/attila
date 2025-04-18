"""add table roles to table users

Revision ID: d995911f8c6e
Revises: 1ca10fc08bd5
Create Date: 2025-04-18 17:23:20.893180

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'd995911f8c6e'
down_revision = '1ca10fc08bd5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.Integer(), nullable=False, unique=True),
    )

    # many-to-many relationship : users_to_roles
    op.create_table(
        'users_to_roles',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    )

def downgrade():
    op.drop_table('users_to_roles')
    op.drop_table('roles')