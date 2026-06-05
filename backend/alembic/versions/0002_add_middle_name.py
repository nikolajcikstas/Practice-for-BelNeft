"""add middle_name to employees

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-05
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("employees", sa.Column("middle_name", sa.String(100), nullable=True))


def downgrade() -> None:
    op.drop_column("employees", "middle_name")
