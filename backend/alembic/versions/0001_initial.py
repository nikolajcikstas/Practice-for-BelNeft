"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-05
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("position", sa.String(200), nullable=False),
        sa.Column("photo_url", sa.String(500), nullable=True),
        sa.Column("date_added", sa.Date(), nullable=False),
        sa.UniqueConstraint("last_name", "first_name", name="uq_employee_name"),
    )
    op.create_index("ix_employees_last_name", "employees", ["last_name"])
    op.create_index("ix_employees_first_name", "employees", ["first_name"])

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.UniqueConstraint("name", name="uq_skill_name"),
    )
    op.create_index("ix_skills_name", "skills", ["name"])
    op.create_index("ix_skills_category", "skills", ["category"])

    op.create_table(
        "employee_skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("proficiency_level", sa.Integer(), nullable=False),
        sa.UniqueConstraint("employee_id", "skill_id", name="uq_employee_skill"),
        sa.CheckConstraint("proficiency_level >= 0 AND proficiency_level <= 5", name="ck_proficiency"),
    )
    op.create_index("ix_employee_skills_employee_id", "employee_skills", ["employee_id"])
    op.create_index("ix_employee_skills_skill_id", "employee_skills", ["skill_id"])

    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False),
        sa.Column("topic", sa.String(300), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_bookings_employee_id", "bookings", ["employee_id"])
    op.create_index("ix_bookings_start_time", "bookings", ["start_time"])
    op.create_index("ix_bookings_end_time", "bookings", ["end_time"])


def downgrade() -> None:
    op.drop_table("bookings")
    op.drop_table("employee_skills")
    op.drop_table("skills")
    op.drop_table("employees")
