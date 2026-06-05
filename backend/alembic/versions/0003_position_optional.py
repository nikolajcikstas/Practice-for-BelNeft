"""position optional, fix employee names

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-05
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("employees", "position", existing_type=sa.String(200), nullable=True)
    op.execute("""
        UPDATE employees
        SET middle_name = TRIM(position), position = NULL
        WHERE (middle_name IS NULL OR TRIM(middle_name) = '')
          AND position IS NOT NULL AND TRIM(position) != ''
    """)
    op.execute("""
        UPDATE employees SET middle_name = '—'
        WHERE middle_name IS NULL OR TRIM(middle_name) = ''
    """)
    op.execute("""
        UPDATE employees SET
          last_name = TRIM(last_name),
          first_name = TRIM(first_name),
          middle_name = TRIM(middle_name),
          position = NULLIF(TRIM(position), '')
    """)


def downgrade() -> None:
    op.alter_column("employees", "position", existing_type=sa.String(200), nullable=False)
