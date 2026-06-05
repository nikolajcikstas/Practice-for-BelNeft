from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = (UniqueConstraint("name", name="uq_skill_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    category: Mapped[str] = mapped_column(String(100), index=True)

    employee_skills: Mapped[list["EmployeeSkill"]] = relationship(
        back_populates="skill", cascade="all, delete-orphan"
    )
