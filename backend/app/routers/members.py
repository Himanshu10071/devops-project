from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from ..db import get_db
from ..models import Member, Plan, Trainer
from ..schemas import MemberCreate, MemberOut, MemberUpdate, MembershipState
from ..services import add_months, membership_state, to_member_out

router = APIRouter(prefix="/api/members", tags=["members"])


def _get_or_404(db: Session, member_id: int) -> Member:
    member = db.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


def _require_plan(db: Session, plan_id: int) -> Plan:
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=422, detail="Selected plan does not exist")
    return plan


def _require_trainer(db: Session, trainer_id: int | None) -> None:
    if trainer_id is not None and not db.get(Trainer, trainer_id):
        raise HTTPException(status_code=422, detail="Selected trainer does not exist")


def _ensure_unique_email(db: Session, email: str, exclude_id: int | None = None) -> None:
    query = select(Member).where(func.lower(Member.email) == email.lower())
    if exclude_id is not None:
        query = query.where(Member.id != exclude_id)
    if db.scalars(query).first():
        raise HTTPException(status_code=409, detail="A member with this email already exists")


@router.get("", response_model=list[MemberOut])
def list_members(
    state: MembershipState | None = Query(default=None, description="Filter by membership state"),
    q: str | None = Query(default=None, description="Search by name, email or phone"),
    db: Session = Depends(get_db),
):
    query = select(Member).options(selectinload(Member.plan), selectinload(Member.trainer)).order_by(Member.id.desc())
    if q:
        like = f"%{q.lower()}%"
        query = query.where(
            or_(func.lower(Member.full_name).like(like), func.lower(Member.email).like(like), Member.phone.like(like))
        )
    members = db.scalars(query).all()
    if state:
        today = date.today()
        members = [m for m in members if membership_state(m, today) == state]
    return [to_member_out(m) for m in members]


@router.get("/{member_id}", response_model=MemberOut)
def get_member(member_id: int, db: Session = Depends(get_db)):
    return to_member_out(_get_or_404(db, member_id))


@router.post("", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def create_member(payload: MemberCreate, db: Session = Depends(get_db)):
    plan = _require_plan(db, payload.plan_id)
    _require_trainer(db, payload.trainer_id)
    _ensure_unique_email(db, payload.email)
    start = payload.start_date or date.today()
    member = Member(
        **payload.model_dump(exclude={"start_date"}),
        start_date=start,
        end_date=add_months(start, plan.duration_months),
        status="ACTIVE",
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return to_member_out(member)


@router.put("/{member_id}", response_model=MemberOut)
def update_member(member_id: int, payload: MemberUpdate, db: Session = Depends(get_db)):
    member = _get_or_404(db, member_id)
    changes = payload.model_dump(exclude_unset=True)
    if "email" in changes:
        _ensure_unique_email(db, changes["email"], exclude_id=member_id)
    if "trainer_id" in changes:
        _require_trainer(db, changes["trainer_id"])
    if changes.get("plan_id") is not None:
        _require_plan(db, changes["plan_id"])
    elif "plan_id" in changes:
        changes.pop("plan_id")  # a member always needs a plan

    for key, value in changes.items():
        setattr(member, key, value)

    # Changing the plan or start date re-computes when the membership ends.
    if "plan_id" in changes or "start_date" in changes:
        plan = db.get(Plan, member.plan_id)
        if plan:
            member.end_date = add_months(member.start_date, plan.duration_months)

    db.commit()
    db.refresh(member)
    return to_member_out(member)


@router.post("/{member_id}/renew", response_model=MemberOut)
def renew_member(member_id: int, db: Session = Depends(get_db)):
    """Extend the membership by one more period of the member's current plan."""
    member = _get_or_404(db, member_id)
    if member.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Cancelled memberships cannot be renewed")
    plan = db.get(Plan, member.plan_id) if member.plan_id else None
    if not plan:
        raise HTTPException(status_code=400, detail="Member has no plan to renew")
    base = max(member.end_date, date.today())
    member.end_date = add_months(base, plan.duration_months)
    member.status = "ACTIVE"
    db.commit()
    db.refresh(member)
    return to_member_out(member)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    member = _get_or_404(db, member_id)
    db.delete(member)
    db.commit()
