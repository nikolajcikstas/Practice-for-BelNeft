from sqlalchemy import CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"
    __table_args__ = (
        UniqueConstraint("employee_id", "skill_id", name="uq_employee_skill"),
        CheckConstraint("proficiency_level >= 0 AND proficiency_level <= 5", name="ck_proficiency"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), index=True
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), index=True
    )
    proficiency_level: Mapped[int] = mapped_column(Integer)

    employee: Mapped["Employee"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship(back_populates="employee_skills")
