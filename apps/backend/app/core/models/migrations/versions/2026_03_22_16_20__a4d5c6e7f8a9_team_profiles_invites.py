"""team profiles, captains, and invite links

Revision ID: a4d5c6e7f8a9
Revises: b7d4f9a2c1e0
Create Date: 2026-03-22 16:20:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a4d5c6e7f8a9"
down_revision: str | None = "b7d4f9a2c1e0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "teams",
        sa.Column("avatar", sa.String(length=2048), nullable=True),
    )
    op.add_column(
        "teams",
        sa.Column("location", sa.String(length=100), nullable=False, server_default=""),
    )
    op.add_column(
        "teams",
        sa.Column(
            "links",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
    )
    op.add_column(
        "teams",
        sa.Column("captain_user_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_teams_captain_user_id_users"),
        "teams",
        "users",
        ["captain_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_teams_captain_user_id"),
        "teams",
        ["captain_user_id"],
        unique=False,
    )

    op.execute(
        sa.text(
            """
            UPDATE teams AS t
            SET captain_user_id = rel.user_id
            FROM (
                SELECT DISTINCT ON (team_id) team_id, user_id
                FROM team_users
                ORDER BY team_id, user_id
            ) AS rel
            WHERE t.id = rel.team_id
              AND t.captain_user_id IS NULL
            """,
        ),
    )

    op.create_table(
        "team_invites",
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_by_user_id", sa.Integer(), nullable=True),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name=op.f("fk_team_invites_created_by_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.id"],
            name=op.f("fk_team_invites_team_id_teams"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["used_by_user_id"],
            ["users.id"],
            name=op.f("fk_team_invites_used_by_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_team_invites")),
        sa.UniqueConstraint("token", name=op.f("uq_team_invites_token")),
    )
    op.create_index(
        op.f("ix_team_invites_team_id"),
        "team_invites",
        ["team_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_team_invites_team_id"), table_name="team_invites")
    op.drop_table("team_invites")

    op.drop_index(op.f("ix_teams_captain_user_id"), table_name="teams")
    op.drop_constraint(
        op.f("fk_teams_captain_user_id_users"),
        "teams",
        type_="foreignkey",
    )
    op.drop_column("teams", "captain_user_id")
    op.drop_column("teams", "links")
    op.drop_column("teams", "location")
    op.drop_column("teams", "avatar")
