"""initial_room_table

Revision ID: 99d44460637b
Revises:
Create Date: 2026-05-10 15:09:48.960157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '99d44460637b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    roomtype = postgresql.ENUM(
        'standard',
        'suite',
        'family',
        name='roomtype',
        create_type=False,
    )
    roomtype.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_number', sa.String(), nullable=False),
        sa.Column('room_type', roomtype, nullable=False),
        sa.Column('price_per_night', sa.Float(), nullable=False),
        sa.Column('floor', sa.Integer(), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('room_number'),
    )


def downgrade() -> None:
    op.drop_table('rooms')
    postgresql.ENUM('standard', 'suite', 'family', name='roomtype').drop(op.get_bind(), checkfirst=True)