from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Plan(Base):
    """A membership plan a member can buy, e.g. Monthly / Quarterly / Annual."""

    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    duration_months: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)  # INR, whole rupees
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    members: Mapped[list["Member"]] = relationship(back_populates="plan")


class Trainer(Base):
    __tablename__ = "trainers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    specialization: Mapped[str] = mapped_column(String(120), default="General Fitness")
    phone: Mapped[str] = mapped_column(String(20), default="")
    email: Mapped[str] = mapped_column(String(160), default="")
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    members: Mapped[list["Member"]] = relationship(back_populates="trainer")


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), default="")
    gender: Mapped[str] = mapped_column(String(10), default="OTHER")
    # ACTIVE / FROZEN / CANCELLED. "Expired" is derived from end_date, not stored.
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    plan_id: Mapped[int | None] = mapped_column(ForeignKey("plans.id", ondelete="SET NULL"), nullable=True)
    trainer_id: Mapped[int | None] = mapped_column(ForeignKey("trainers.id", ondelete="SET NULL"), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    plan: Mapped[Plan | None] = relationship(back_populates="members")
    trainer: Mapped[Trainer | None] = relationship(back_populates="members")
    checkins: Mapped[list["CheckIn"]] = relationship(back_populates="member", cascade="all, delete-orphan")


class CheckIn(Base):
    """One gym visit by a member."""

    __tablename__ = "checkins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)
    checked_in_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    member: Mapped[Member] = relationship(back_populates="checkins")
