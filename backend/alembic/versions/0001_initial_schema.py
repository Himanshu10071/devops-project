"""initial gym schema: plans, trainers, members, checkins"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=80), nullable=False, unique=True),
        sa.Column("duration_months", sa.Integer(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "trainers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("specialization", sa.String(length=120), nullable=False, server_default="General Fitness"),
        sa.Column("phone", sa.String(length=20), nullable=False, server_default=""),
        sa.Column("email", sa.String(length=160), nullable=False, server_default=""),
        sa.Column("experience_years", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=160), nullable=False, unique=True),
        sa.Column("phone", sa.String(length=20), nullable=False, server_default=""),
        sa.Column("gender", sa.String(length=10), nullable=False, server_default="OTHER"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("plans.id", ondelete="SET NULL"), nullable=True),
        sa.Column("trainer_id", sa.Integer(), sa.ForeignKey("trainers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "checkins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("member_id", sa.Integer(), sa.ForeignKey("members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("checked_in_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_checkins_member_id", "checkins", ["member_id"])
    op.create_index("ix_checkins_checked_in_at", "checkins", ["checked_in_at"])


def downgrade():
    op.drop_index("ix_checkins_checked_in_at", table_name="checkins")
    op.drop_index("ix_checkins_member_id", table_name="checkins")
    op.drop_table("checkins")
    op.drop_table("members")
    op.drop_table("trainers")
    op.drop_table("plans")
