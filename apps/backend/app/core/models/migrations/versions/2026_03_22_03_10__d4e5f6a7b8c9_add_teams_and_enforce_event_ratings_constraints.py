"""add teams and enforce event ratings constraints

Revision ID: d4e5f6a7b8c9
Revises: a1b2c3d4e5f6
Create Date: 2026-03-22 03:10:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_teams")),
        sa.UniqueConstraint("name", name=op.f("uq_teams_name")),
    )

    op.create_table(
        "team_users",
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.id"],
            name=op.f("fk_team_users_team_id_teams"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_team_users_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("team_id", "user_id"),
    )

    op.execute(
        sa.text(
            """
            UPDATE event_ratings
            SET status = 'participant'
            WHERE status NOT IN ('winner', 'prize_winner', 'participant')
            """,
        ),
    )

    op.create_check_constraint(
        op.f("ck_event_ratings_status_allowed"),
        "event_ratings",
        "status IN ('winner', 'prize_winner', 'participant')",
    )

    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM event_ratings er
                    WHERE er.team_id IS NOT NULL
                      AND NOT EXISTS (
                          SELECT 1
                          FROM teams t
                          WHERE t.id = er.team_id
                      )
                ) THEN
                    RAISE EXCEPTION
                        'Migration requires manual data prep: '
                        'orphan event_ratings.team_id detected';
                END IF;
            END $$;
            """,
        ),
    )

    op.create_foreign_key(
        op.f("fk_event_ratings_team_id_teams"),
        "event_ratings",
        "teams",
        ["team_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_event_ratings_team_id_teams"),
        "event_ratings",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("ck_event_ratings_status_allowed"),
        "event_ratings",
        type_="check",
    )
    op.drop_table("team_users")
    op.drop_table("teams")
