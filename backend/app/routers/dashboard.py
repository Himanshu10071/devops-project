from datetime import date, datetime, time, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..db import get_db
from ..models import CheckIn, Member, Plan, Trainer
from ..schemas import DashboardStats, PlanBreakdown
from ..services import membership_state

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def stats(db: Session = Depends(get_db)):
    today = date.today()
    members = db.scalars(select(Member).options(selectinload(Member.plan))).all()
    states = [membership_state(m, today) for m in members]

    # Recurring revenue: each paying member contributes plan price spread over its months.
    monthly_revenue = sum(
        m.plan.price // m.plan.duration_months
        for m, s in zip(members, states)
        if m.plan and s in ("ACTIVE", "EXPIRING_SOON")
    )

    start_of_day = datetime.combine(today, time.min, tzinfo=timezone.utc)
    checkins_today = db.scalar(select(func.count(CheckIn.id)).where(CheckIn.checked_in_at >= start_of_day)) or 0

    breakdown_rows = db.execute(
        select(Plan.name, func.count(Member.id)).outerjoin(Member, Member.plan_id == Plan.id).group_by(Plan.id, Plan.name).order_by(Plan.duration_months)
    ).all()

    return DashboardStats(
        total_members=len(members),
        active_members=sum(s in ("ACTIVE", "EXPIRING_SOON") for s in states),
        expiring_soon=states.count("EXPIRING_SOON"),
        expired_members=states.count("EXPIRED"),
        frozen_members=states.count("FROZEN"),
        checkins_today=checkins_today,
        trainers=db.scalar(select(func.count(Trainer.id))) or 0,
        plans=len(breakdown_rows),
        monthly_revenue=monthly_revenue,
        plan_breakdown=[PlanBreakdown(plan=name, members=count) for name, count in breakdown_rows],
    )
