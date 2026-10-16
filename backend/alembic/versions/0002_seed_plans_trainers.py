"""seed default membership plans and trainers"""
from alembic import op
import sqlalchemy as sa

revision = "0002_seed_plans_trainers"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None

plans = sa.table(
    "plans",
    sa.column("name", sa.String),
    sa.column("duration_months", sa.Integer),
    sa.column("price", sa.Integer),
    sa.column("description", sa.Text),
)
trainers = sa.table(
    "trainers",
    sa.column("name", sa.String),
    sa.column("specialization", sa.String),
    sa.column("phone", sa.String),
    sa.column("email", sa.String),
    sa.column("experience_years", sa.Integer),
)

PLAN_NAMES = ["Monthly", "Quarterly", "Half-Yearly", "Annual"]
TRAINER_EMAILS = ["rohit@ironpulse.fit", "priya@ironpulse.fit", "arjun@ironpulse.fit"]


def upgrade():
    op.bulk_insert(
        plans,
        [
            {"name": "Monthly", "duration_months": 1, "price": 1500, "description": "Full gym floor access"},
            {"name": "Quarterly", "duration_months": 3, "price": 4000, "description": "Gym floor + 1 diet consultation"},
            {"name": "Half-Yearly", "duration_months": 6, "price": 7500, "description": "Gym floor + group classes"},
            {"name": "Annual", "duration_months": 12, "price": 13000, "description": "All access + personal trainer intro"},
        ],
    )
    op.bulk_insert(
        trainers,
        [
            {"name": "Rohit Sharma", "specialization": "Strength & Conditioning", "phone": "9876500001", "email": TRAINER_EMAILS[0], "experience_years": 6},
            {"name": "Priya Nair", "specialization": "Yoga & Mobility", "phone": "9876500002", "email": TRAINER_EMAILS[1], "experience_years": 4},
            {"name": "Arjun Mehta", "specialization": "CrossFit & HIIT", "phone": "9876500003", "email": TRAINER_EMAILS[2], "experience_years": 8},
        ],
    )


def downgrade():
    op.execute(trainers.delete().where(sa.column("email").in_(TRAINER_EMAILS)))
    op.execute(plans.delete().where(sa.column("name").in_(PLAN_NAMES)))
