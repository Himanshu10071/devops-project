from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Member, Plan
from ..schemas import PlanCreate, PlanOut, PlanUpdate

router = APIRouter(prefix="/api/plans", tags=["plans"])


def _get_or_404(db: Session, plan_id: int) -> Plan:
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


def _ensure_unique_name(db: Session, name: str, exclude_id: int | None = None) -> None:
    query = select(Plan).where(func.lower(Plan.name) == name.lower())
    if exclude_id is not None:
        query = query.where(Plan.id != exclude_id)
    if db.scalars(query).first():
        raise HTTPException(status_code=409, detail="A plan with this name already exists")


@router.get("", response_model=list[PlanOut])
def list_plans(db: Session = Depends(get_db)):
    return list(db.scalars(select(Plan).order_by(Plan.duration_months, Plan.price)))


@router.get("/{plan_id}", response_model=PlanOut)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, plan_id)


@router.post("", response_model=PlanOut, status_code=status.HTTP_201_CREATED)
def create_plan(payload: PlanCreate, db: Session = Depends(get_db)):
    _ensure_unique_name(db, payload.name)
    plan = Plan(**payload.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.put("/{plan_id}", response_model=PlanOut)
def update_plan(plan_id: int, payload: PlanUpdate, db: Session = Depends(get_db)):
    plan = _get_or_404(db, plan_id)
    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes:
        _ensure_unique_name(db, changes["name"], exclude_id=plan_id)
    for key, value in changes.items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = _get_or_404(db, plan_id)
    in_use = db.scalar(select(func.count(Member.id)).where(Member.plan_id == plan_id))
    if in_use:
        raise HTTPException(status_code=409, detail=f"Plan is used by {in_use} member(s); move them first")
    db.delete(plan)
    db.commit()
