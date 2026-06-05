from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user_id
from app.config import settings
from app.database import get_db
from app.models.employee import Employee
from app.models.employee_skill import EmployeeSkill
from app.models.skill import Skill
from app.schemas import (
    EmployeeCreate,
    EmployeeList,
    EmployeeOut,
    EmployeeSkillAssign,
    EmployeeSkillUpdate,
    EmployeeUpdate,
    SkillShort,
)

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=EmployeeList)
def list_employees(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.query(Employee).count()
    employees = (
        db.query(Employee)
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return EmployeeList(items=employees, total=total, page=page, size=size)


@router.post("", response_model=EmployeeOut, status_code=201)
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    emp = Employee(**data.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@router.get("/{emp_id}", response_model=EmployeeOut)
def get_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = db.get(Employee, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@router.patch("/{emp_id}", response_model=EmployeeOut)
def update_employee(
    emp_id: int,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    emp = db.get(Employee, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(emp, field, value)
    db.commit()
    db.refresh(emp)
    return emp


@router.delete("/{emp_id}", status_code=204)
def delete_employee(
    emp_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    if user_id not in settings.admin_ids:
        raise HTTPException(status_code=403, detail="Only admins can delete employees")
    emp = db.get(Employee, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(emp)
    db.commit()


@router.post("/{emp_id}/skills", response_model=SkillShort, status_code=201)
def assign_skill(
    emp_id: int,
    data: EmployeeSkillAssign,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    emp = db.get(Employee, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    skill = db.get(Skill, data.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    existing = (
        db.query(EmployeeSkill)
        .filter_by(employee_id=emp_id, skill_id=data.skill_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Skill already assigned to this employee")

    es = EmployeeSkill(
        employee_id=emp_id,
        skill_id=data.skill_id,
        proficiency_level=data.proficiency_level,
    )
    db.add(es)
    db.commit()
    db.refresh(es)

    return SkillShort(
        id=es.id,
        skill_id=es.skill_id,
        name=skill.name,
        category=skill.category,
        proficiency_level=es.proficiency_level,
    )


@router.patch("/{emp_id}/skills/{skill_id}", response_model=SkillShort)
def update_skill_level(
    emp_id: int,
    skill_id: int,
    data: EmployeeSkillUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    es = (
        db.query(EmployeeSkill)
        .filter_by(employee_id=emp_id, skill_id=skill_id)
        .first()
    )
    if not es:
        raise HTTPException(status_code=404, detail="Skill assignment not found")

    es.proficiency_level = data.proficiency_level
    db.commit()
    db.refresh(es)

    skill = db.get(Skill, skill_id)
    return SkillShort(
        id=es.id,
        skill_id=es.skill_id,
        name=skill.name,
        category=skill.category,
        proficiency_level=es.proficiency_level,
    )


@router.get("/{emp_id}/skills", response_model=list[SkillShort])
def get_employee_skills(emp_id: int, db: Session = Depends(get_db)):
    emp = db.get(Employee, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    rows = (
        db.query(EmployeeSkill, Skill)
        .join(Skill, EmployeeSkill.skill_id == Skill.id)
        .filter(EmployeeSkill.employee_id == emp_id)
        .all()
    )
    return [
        SkillShort(
            id=es.id,
            skill_id=es.skill_id,
            name=skill.name,
            category=skill.category,
            proficiency_level=es.proficiency_level,
        )
        for es, skill in rows
    ]
