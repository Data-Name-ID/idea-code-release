# ingest public api changes

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b7d4f9a2c1e0"
down_revision: str | None = "91f53ebe3814"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "events",
        sa.Column("external_id", sa.String(length=100), nullable=True),
    )
    op.create_unique_constraint(
        op.f("uq_events_external_id"),
        "events",
        ["external_id"],
    )

    op.add_column(
        "teams",
        sa.Column("external_id", sa.String(length=100), nullable=True),
    )
    op.create_unique_constraint(
        op.f("uq_teams_external_id"),
        "teams",
        ["external_id"],
    )

    op.add_column(
        "event_ratings",
        sa.Column("place", sa.Integer(), nullable=True),
    )
    op.create_check_constraint(
        op.f("ck_event_ratings_place_positive"),
        "event_ratings",
        "place IS NULL OR place > 0",
    )

    op.create_table(
        "organizer_api_tokens",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organizer_api_tokens")),
        sa.UniqueConstraint(
            "token_hash",
            name=op.f("uq_organizer_api_tokens_token_hash"),
        ),
    )


def downgrade() -> None:
    op.drop_table("organizer_api_tokens")

    op.drop_constraint(
        op.f("ck_event_ratings_place_positive"),
        "event_ratings",
        type_="check",
    )
    op.drop_column("event_ratings", "place")

    op.drop_constraint(op.f("uq_teams_external_id"), "teams", type_="unique")
    op.drop_column("teams", "external_id")

    op.drop_constraint(op.f("uq_events_external_id"), "events", type_="unique")
    op.drop_column("events", "external_id")
