"""add_bookings_table

Revision ID: 2f8e9c1a4b7d
Revises: 99d44460637b
Create Date: 2026-05-10 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '2f8e9c1a4b7d'
down_revision: Union[str, None] = '99d44460637b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    season = postgresql.ENUM(
        'peak',
        'shoulder',
        'off_season',
        'normal',
        name='season',
        create_type=False,
    )
    season.create(op.get_bind(), checkfirst=True)

    extraservice = postgresql.ENUM(
        'breakfast',
        'parking',
        'spa',
        name='extraservice',
        create_type=False,
    )
    extraservice.create(op.get_bind(), checkfirst=True)

    bookingstatus = postgresql.ENUM(
        'pending',
        'confirmed',
        'cancelled',
        name='bookingstatus',
        create_type=False,
    )
    bookingstatus.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('guest_name', sa.String(), nullable=False),
        sa.Column('guest_email', sa.String(), nullable=False),
        sa.Column('guests_count', sa.Integer(), nullable=False),
        sa.Column('check_in', sa.Date(), nullable=False),
        sa.Column('check_out', sa.Date(), nullable=False),
        sa.Column('season', season, nullable=False),
        sa.Column('extra_service', extraservice, nullable=True),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('status', bookingstatus, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index('ix_bookings_check_in', 'bookings', ['check_in'])
    op.create_index('ix_bookings_check_out', 'bookings', ['check_out'])
    op.create_index('ix_bookings_created_at', 'bookings', ['created_at'])
    op.create_index('ix_bookings_guest_email', 'bookings', ['guest_email'])
    op.create_index('ix_bookings_room_id', 'bookings', ['room_id'])
    op.create_index('ix_bookings_status', 'bookings', ['status'])
    op.create_index(
        'ix_booking_dates',
        'bookings',
        ['check_in', 'check_out'],
    )
    op.create_index(
        'ix_booking_room_dates',
        'bookings',
        ['room_id', 'check_in', 'check_out'],
    )
    op.create_index(
        'ix_booking_guest_created',
        'bookings',
        ['guest_email', 'created_at'],
    )


def downgrade() -> None:
    op.drop_index('ix_booking_guest_created', table_name='bookings')
    op.drop_index('ix_booking_room_dates', table_name='bookings')
    op.drop_index('ix_booking_dates', table_name='bookings')
    op.drop_index('ix_bookings_status', table_name='bookings')
    op.drop_index('ix_bookings_room_id', table_name='bookings')
    op.drop_index('ix_bookings_guest_email', table_name='bookings')
    op.drop_index('ix_bookings_created_at', table_name='bookings')
    op.drop_index('ix_bookings_check_out', table_name='bookings')
    op.drop_index('ix_bookings_check_in', table_name='bookings')

    op.drop_table('bookings')

    postgresql.ENUM('pending', 'confirmed', 'cancelled', name='bookingstatus').drop(
        op.get_bind(), checkfirst=True
    )
    postgresql.ENUM('breakfast', 'parking', 'spa', name='extraservice').drop(
        op.get_bind(), checkfirst=True
    )
    postgresql.ENUM('peak', 'shoulder', 'off_season', 'normal', name='season').drop(
        op.get_bind(), checkfirst=True
    )
