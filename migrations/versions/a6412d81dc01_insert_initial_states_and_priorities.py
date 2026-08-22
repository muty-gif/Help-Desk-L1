"""Insert initial states and priorities

Revision ID: a6412d81dc01
Revises: 3fec83ec070b
Create Date: 2026-08-22 11:48:56.744438

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6412d81dc01'
down_revision = '3fec83ec070b'
branch_labels = None
depends_on = None


def upgrade():
    states_table = sa.table(
        "states",
        sa.column("name", sa.String(length=50))
    )
    
    priorities_table = sa.table(
        "priorities",
        sa.column("name", sa.String(length=50))
    )

    op.bulk_insert(
        states_table,
        [
            {"name": "Abierto"},
            {"name": "En progreso"},
            {"name": "Pendiente"},
            {"name": "Resuelto"},
            {"name": "Cerrado"},
        ]
    )
    
    op.bulk_insert(
        priorities_table,
        [
            {"name": "Baja"},
            {"name": "Media"},
            {"name": "Alta"},
            {"name": "Crítica"},
        ]
    )


def downgrade():
    op.execute(
        """
        DELETE FROM states
        WHERE name IN (
            'Abierto',
            'En progreso',
            'Pendiente',
            'Resuelto',
            'Cerrado'
        )
        """
    )

    op.execute(
        """
        DELETE FROM priorities
        WHERE name IN (
            'Baja',
            'Media',
            'Alta',
            'Crítica'
        )
        """
    )