# participation applications and teammate search fields

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c4b8d2a1e9f1"
down_revision: str | None = "bfbe2be8b666"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "open_to_teamup",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.alter_column("users", "open_to_teamup", server_default=None)

    op.create_table(
        "participation_applications",
        sa.Column("applicant_user_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("comment", sa.String(length=1000), nullable=False),
        sa.Column("desired_role", sa.String(length=100), nullable=False),
        sa.Column("preferred_team_format", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name=op.f("ck_participation_applications_status_allowed"),
        ),
        sa.CheckConstraint(
            "preferred_team_format IN ('solo', 'team')",
            name=op.f("ck_participation_applications_preferred_team_format_allowed"),
        ),
        sa.ForeignKeyConstraint(
            ["applicant_user_id"],
            ["users.id"],
            name=op.f("fk_participation_applications_applicant_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["events.id"],
            name=op.f("fk_participation_applications_event_id_events"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_participation_applications")),
    )

    op.create_table(
        "participation_application_skills",
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["participation_applications.id"],
            name=op.f(
                "fk_participation_application_skills_application_id_participation_applications",
            ),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"],
            ["skills.id"],
            name=op.f("fk_participation_application_skills_skill_id_skills"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "application_id",
            "skill_id",
            name=op.f("pk_participation_application_skills"),
        ),
    )


def downgrade() -> None:
    op.drop_table("participation_application_skills")
    op.drop_table("participation_applications")

    op.drop_column("users", "open_to_teamup")
