"""empty message

Revision ID: d599cee1ac7f
Revises: 
Create Date: 2018-11-18 10:15:37.980971

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd599cee1ac7f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('balance', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_account_name'), 'account', ['name'], unique=True)
    op.create_table('trade',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('stock', sa.String(length=64), nullable=True),
    sa.Column('volume', sa.Integer(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trade_stock'), 'trade', ['stock'], unique=False)
    op.create_index(op.f('ix_trade_timestamp'), 'trade', ['timestamp'], unique=False)
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.Column('stock', sa.String(length=64), nullable=True),
    sa.Column('type', sa.String(length=8), nullable=True),
    sa.Column('side', sa.String(length=8), nullable=True),
    sa.Column('volume', sa.Integer(), nullable=True),
    sa.Column('limit', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_limit'), 'order', ['limit'], unique=False)
    op.create_index(op.f('ix_order_side'), 'order', ['side'], unique=False)
    op.create_index(op.f('ix_order_stock'), 'order', ['stock'], unique=False)
    op.create_index(op.f('ix_order_timestamp'), 'order', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_order_timestamp'), table_name='order')
    op.drop_index(op.f('ix_order_stock'), table_name='order')
    op.drop_index(op.f('ix_order_side'), table_name='order')
    op.drop_index(op.f('ix_order_limit'), table_name='order')
    op.drop_table('order')
    op.drop_index(op.f('ix_trade_timestamp'), table_name='trade')
    op.drop_index(op.f('ix_trade_stock'), table_name='trade')
    op.drop_table('trade')
    op.drop_index(op.f('ix_account_name'), table_name='account')
    op.drop_table('account')
    # ### end Alembic commands ###
