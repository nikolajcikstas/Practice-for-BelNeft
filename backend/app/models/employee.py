from datetime import date

from sqlalchemy import Date, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (UniqueConstraint("last_name", "first_name", name="uq_employee_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    last_name: Mapped[str] = mapped_column(String(100), index=True)
    first_name: Mapped[str] = mapped_column(String(100), index=True)
    position: Mapped[str] = mapped_column(String(200))
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    date_added: Mapped[date] = mapped_column(Date, default=date.today)

    skills: Mapped[list["EmployeeSkill"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )
    bookings: Mapped[list["Booking"]] = relationship(back_populates="employee")
