from fastapi import APIRouter, Depends, HTTPException, Query, status
from prometheus_client import Counter
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..db import get_db
from ..models import CheckIn, Member
from ..schemas import CheckInCreate, CheckInOut
from ..services import membership_state

router = APIRouter(prefix="/api/checkins", tags=["attendance"])

# Business metric scraped by Prometheus next to the HTTP metrics.
CHECKINS_TOTAL = Counter("gym_checkins_total", "Successful member check-ins", ["result"])


def _to_out(checkin: CheckIn) -> CheckInOut:
    return CheckInOut(
        id=checkin.id,
        member_id=checkin.member_id,
        member_name=checkin.member.full_name,
        checked_in_at=checkin.checked_in_at,
    )


@router.get("", response_model=list[CheckInOut])
def list_checkins(
    limit: int = Query(default=20, ge=1, le=200),
    member_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = select(CheckIn).options(selectinload(CheckIn.member)).order_by(CheckIn.checked_in_at.desc(), CheckIn.id.desc())
    if member_id is not None:
        query = query.where(CheckIn.member_id == member_id)
    return [_to_out(c) for c in db.scalars(query.limit(limit))]


@router.post("", response_model=CheckInOut, status_code=status.HTTP_201_CREATED)
def create_checkin(payload: CheckInCreate, db: Session = Depends(get_db)):
    member = db.get(Member, payload.member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    state = membership_state(member)
    if state not in ("ACTIVE", "EXPIRING_SOON"):
        CHECKINS_TOTAL.labels(result="rejected").inc()
        raise HTTPException(status_code=400, detail=f"Check-in refused: membership is {state.lower()}")
    checkin = CheckIn(member_id=member.id)
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    CHECKINS_TOTAL.labels(result="accepted").inc()
    return _to_out(checkin)
