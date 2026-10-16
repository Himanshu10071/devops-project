"""Business rules shared by the routers: membership dates and state."""
import calendar
from datetime import date

from .config import settings
from .models import Member
from .schemas import MemberOut


def add_months(start: date, months: int) -> date:
    """Add calendar months, clamping the day (Jan 31 + 1 month -> Feb 28/29)."""
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def membership_state(member: Member, today: date | None = None) -> str:
    today = today or date.today()
    if member.status in ("FROZEN", "CANCELLED"):
        return member.status
    if member.end_date < today:
        return "EXPIRED"
    if (member.end_date - today).days <= settings.expiring_soon_days:
        return "EXPIRING_SOON"
    return "ACTIVE"


def to_member_out(member: Member) -> MemberOut:
    today = date.today()
    return MemberOut(
        id=member.id,
        full_name=member.full_name,
        email=member.email,
        phone=member.phone,
        gender=member.gender,
        status=member.status,
        membership_state=membership_state(member, today),
        plan_id=member.plan_id,
        plan_name=member.plan.name if member.plan else None,
        trainer_id=member.trainer_id,
        trainer_name=member.trainer.name if member.trainer else None,
        start_date=member.start_date,
        end_date=member.end_date,
        days_left=max((member.end_date - today).days, 0),
        created_at=member.created_at,
    )
