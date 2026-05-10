"""add_room_indexes

Revision ID: a1b2c3d4e5f6
Revises: 2f8e9c1a4b7d
Create Date: 2026-05-10 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '2f8e9c1a4b7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE INDEX IF NOT EXISTS ix_rooms_capacity ON rooms (capacity)')
    op.execute('CREATE INDEX IF NOT EXISTS ix_rooms_floor ON rooms (floor)')
    op.execute('CREATE INDEX IF NOT EXISTS ix_rooms_price_per_night ON rooms (price_per_night)')
    op.execute('CREATE INDEX IF NOT EXISTS ix_rooms_room_number ON rooms (room_number)')
    op.execute('CREATE INDEX IF NOT EXISTS ix_rooms_room_type ON rooms (room_type)')
    op.execute('CREATE INDEX IF NOT EXISTS ix_room_type_price ON rooms (room_type, price_per_night)')


def downgrade() -> None:
    op.drop_index('ix_room_type_price', table_name='rooms')
    op.drop_index('ix_rooms_room_type', table_name='rooms')
    op.drop_index('ix_rooms_room_number', table_name='rooms')
    op.drop_index('ix_rooms_price_per_night', table_name='rooms')
    op.drop_index('ix_rooms_floor', table_name='rooms')
    op.drop_index('ix_rooms_capacity', table_name='rooms')
