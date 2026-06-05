from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


# --- Employee ---

class EmployeeBase(BaseModel):
    last_name: str = Field(..., min_length=1, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: str = Field(..., min_length=1, max_length=100)
    position: str | None = Field(None, max_length=200)
    photo_url: str | None = None

    @field_validator("position", mode="before")
    @classmethod
    def empty_position_to_none(cls, value):
        if value is not None and not str(value).strip():
            return None
        return value


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    last_name: str | None = Field(None, min_length=1, max_length=100)
    first_name: str | None = Field(None, min_length=1, max_length=100)
    middle_name: str | None = Field(None, min_length=1, max_length=100)
    position: str | None = Field(None, max_length=200)
    photo_url: str | None = None


class SkillShort(BaseModel):
    id: int
    skill_id: int
    name: str
    category: str
    proficiency_level: int

    model_config = {"from_attributes": True}


class EmployeeOut(EmployeeBase):
    id: int
    date_added: date
    skills: list[SkillShort] = []

    model_config = {"from_attributes": True}


class EmployeeList(BaseModel):
    items: list[EmployeeOut]
    total: int
    page: int
    size: int


# --- Skill ---

class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    category: str = Field(..., min_length=1, max_length=100)


class SkillOut(BaseModel):
    id: int
    name: str
    category: str

    model_config = {"from_attributes": True}


# --- EmployeeSkill ---

class EmployeeSkillAssign(BaseModel):
    skill_id: int
    proficiency_level: int = Field(..., ge=0, le=5)


class EmployeeSkillUpdate(BaseModel):
    proficiency_level: int = Field(..., ge=0, le=5)


# --- Booking ---

class BookingCreate(BaseModel):
    employee_id: int
    topic: str = Field(..., min_length=1, max_length=300)
    start_time: datetime
    end_time: datetime

    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, v, info):
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class BookingOut(BaseModel):
    id: int
    employee_id: int
    employee_name: str | None = None
    employee_photo_url: str | None = None
    topic: str
    start_time: datetime
    end_time: datetime

    model_config = {"from_attributes": True}
