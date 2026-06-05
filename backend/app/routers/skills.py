from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user_id
from app.database import get_db
from app.models.skill import Skill
from app.schemas import SkillCreate, SkillOut

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillOut])
def list_skills(db: Session = Depends(get_db)):
    return db.query(Skill).order_by(Skill.category, Skill.name).all()


@router.post("", response_model=SkillOut, status_code=201)
def create_skill(
    data: SkillCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    existing = db.query(Skill).filter_by(name=data.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Skill with this name already exists")
    skill = Skill(**data.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill
