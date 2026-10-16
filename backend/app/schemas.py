from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Gender = Literal["MALE", "FEMALE", "OTHER"]
MemberStatus = Literal["ACTIVE", "FROZEN", "CANCELLED"]
# What the UI shows: stored status combined with the expiry date.
MembershipState = Literal["ACTIVE", "EXPIRING_SOON", "EXPIRED", "FROZEN", "CANCELLED"]


# ---------- Plans ----------
class PlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    duration_months: int = Field(ge=1, le=36)
    price: int = Field(ge=0)
    description: str = ""


class PlanUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    duration_months: int | None = Field(default=None, ge=1, le=36)
    price: int | None = Field(default=None, ge=0)
    description: str | None = None


class PlanOut(PlanCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------- Trainers ----------
class TrainerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    specialization: str = "General Fitness"
    phone: str = Field(default="", max_length=20)
    email: str = Field(default="", max_length=160)
    experience_years: int = Field(default=0, ge=0, le=60)


class TrainerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    specialization: str | None = None
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=160)
    experience_years: int | None = Field(default=None, ge=0, le=60)


class TrainerOut(TrainerCreate):
    id: int
    member_count: int = 0
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------- Members ----------
class MemberCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    phone: str = Field(default="", max_length=20)
    gender: Gender = "OTHER"
    plan_id: int
    trainer_id: int | None = None
    start_date: date | None = None  # defaults to today


class MemberUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    gender: Gender | None = None
    status: MemberStatus | None = None
    plan_id: int | None = None
    trainer_id: int | None = None
    start_date: date | None = None


class MemberOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    gender: Gender
    status: MemberStatus
    membership_state: MembershipState
    plan_id: int | None
    plan_name: str | None
    trainer_id: int | None
    trainer_name: str | None
    start_date: date
    end_date: date
    days_left: int
    created_at: datetime


# ---------- Check-ins ----------
class CheckInCreate(BaseModel):
    member_id: int


class CheckInOut(BaseModel):
    id: int
    member_id: int
    member_name: str
    checked_in_at: datetime


# ---------- Dashboard ----------
class PlanBreakdown(BaseModel):
    plan: str
    members: int


class DashboardStats(BaseModel):
    total_members: int
    active_members: int
    expiring_soon: int
    expired_members: int
    frozen_members: int
    checkins_today: int
    trainers: int
    plans: int
    monthly_revenue: int
    plan_breakdown: list[PlanBreakdown]
