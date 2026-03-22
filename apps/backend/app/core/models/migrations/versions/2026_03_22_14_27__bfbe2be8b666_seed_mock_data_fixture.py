# seed mock data fixture

import os
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import Connection

from app.core.models.migrations.fixtures.mock_data import (
    EVENT_RATINGS,
    EVENTS,
    ROLES,
    SKILLS,
    TEAM_MEMBERSHIPS,
    TEAMS,
    TELEGRAM_IDENTITIES,
    USER_ROLES,
    USER_SKILLS,
    USERS,
)

revision: str = "bfbe2be8b666"
down_revision: str | None = "b7d4f9a2c1e0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

roles_table = sa.table(
    "roles",
    sa.column("id", sa.Integer()),
    sa.column("name", sa.String(length=100)),
)

skills_table = sa.table(
    "skills",
    sa.column("id", sa.Integer()),
    sa.column("name", sa.String(length=100)),
)

users_table = sa.table(
    "users",
    sa.column("id", sa.Integer()),
    sa.column("username", sa.String(length=100)),
    sa.column("email", sa.String(length=255)),
    sa.column("name", sa.String(length=100)),
    sa.column("avatar", sa.String(length=2048)),
    sa.column("description", sa.String(length=1000)),
    sa.column("location", sa.String(length=100)),
    sa.column("links", JSONB(astext_type=sa.Text())),
    sa.column("activated", sa.Boolean()),
    sa.column("created_at", sa.DateTime(timezone=True)),
    sa.column("updated_at", sa.DateTime(timezone=True)),
)

teams_table = sa.table(
    "teams",
    sa.column("id", sa.Integer()),
    sa.column("name", sa.String(length=100)),
    sa.column("description", sa.String(length=1000)),
    sa.column("created_at", sa.DateTime(timezone=True)),
    sa.column("updated_at", sa.DateTime(timezone=True)),
)

events_table = sa.table(
    "events",
    sa.column("id", sa.Integer()),
    sa.column("title", sa.String(length=100)),
    sa.column("description", sa.String(length=1000)),
    sa.column("date", sa.DateTime(timezone=True)),
    sa.column("cover", sa.String(length=2048)),
    sa.column("is_verify", sa.Boolean()),
    sa.column("created_at", sa.DateTime(timezone=True)),
    sa.column("updated_at", sa.DateTime(timezone=True)),
)

team_users_table = sa.table(
    "team_users",
    sa.column("team_id", sa.Integer()),
    sa.column("user_id", sa.Integer()),
)

user_roles_table = sa.table(
    "user_roles",
    sa.column("user_id", sa.Integer()),
    sa.column("role_id", sa.Integer()),
)

user_skills_table = sa.table(
    "user_skills",
    sa.column("user_id", sa.Integer()),
    sa.column("skill_id", sa.Integer()),
)

event_ratings_table = sa.table(
    "event_ratings",
    sa.column("event_id", sa.Integer()),
    sa.column("user_id", sa.Integer()),
    sa.column("status", sa.String(length=20)),
    sa.column("team_id", sa.Integer()),
    sa.column("awarded_at", sa.DateTime(timezone=True)),
)

telegram_identities_table = sa.table(
    "telegram_identities",
    sa.column("id", sa.Integer()),
    sa.column("user_id", sa.Integer()),
    sa.column("telegram_user_id", sa.BigInteger()),
    sa.column("username", sa.String(length=100)),
    sa.column("first_name", sa.String(length=100)),
    sa.column("last_name", sa.String(length=100)),
    sa.column("photo_url", sa.String(length=2048)),
    sa.column("auth_date", sa.DateTime(timezone=True)),
    sa.column("created_at", sa.DateTime(timezone=True)),
    sa.column("updated_at", sa.DateTime(timezone=True)),
)


def _is_mock_data_allowed() -> bool:
    raw_flag = os.getenv("APP_MIGRATION_ALLOW_MOCK_DATA", "")
    return raw_flag.strip().lower() in {"1", "true", "yes", "y", "on"}


def _insert_events(connection: Connection) -> None:
    for event in EVENTS:
        exists_stmt = sa.exists(
            sa.select(events_table.c.id).where(events_table.c.title == event["title"]),
        )
        insert_stmt = sa.insert(events_table).from_select(
            [
                events_table.c.title,
                events_table.c.description,
                events_table.c.date,
                events_table.c.cover,
                events_table.c.is_verify,
                events_table.c.created_at,
                events_table.c.updated_at,
            ],
            sa.select(
                sa.literal(event["title"]),
                sa.literal(event["description"]),
                sa.literal(event["date"]),
                sa.literal(event["cover"]),
                sa.literal(event["is_verify"]),
                sa.literal(event["created_at"]),
                sa.literal(event["updated_at"]),
            ).where(sa.not_(exists_stmt)),
        )
        connection.execute(insert_stmt)


def _insert_team_memberships(connection: Connection) -> None:
    membership_values = sa.values(
        sa.column("team_name", sa.String(length=100)),
        sa.column("username", sa.String(length=100)),
        name="mock_team_memberships_values",
    ).data([(item["team_name"], item["username"]) for item in TEAM_MEMBERSHIPS])
    membership_select = sa.select(
        teams_table.c.id.label("team_id"),
        users_table.c.id.label("user_id"),
    ).select_from(
        membership_values.join(
            teams_table, teams_table.c.name == membership_values.c.team_name,
        ).join(users_table, users_table.c.username == membership_values.c.username),
    )
    connection.execute(
        pg_insert(team_users_table)
        .from_select(
            [
                team_users_table.c.team_id,
                team_users_table.c.user_id,
            ],
            membership_select,
        )
        .on_conflict_do_nothing(
            index_elements=[team_users_table.c.team_id, team_users_table.c.user_id],
        ),
    )


def _insert_user_roles(connection: Connection) -> None:
    role_values = sa.values(
        sa.column("username", sa.String(length=100)),
        sa.column("role_name", sa.String(length=100)),
        name="mock_user_roles_values",
    ).data([(item["username"], item["role_name"]) for item in USER_ROLES])
    role_select = sa.select(
        users_table.c.id.label("user_id"),
        roles_table.c.id.label("role_id"),
    ).select_from(
        role_values.join(
            users_table, users_table.c.username == role_values.c.username,
        ).join(roles_table, roles_table.c.name == role_values.c.role_name),
    )
    connection.execute(
        pg_insert(user_roles_table)
        .from_select(
            [
                user_roles_table.c.user_id,
                user_roles_table.c.role_id,
            ],
            role_select,
        )
        .on_conflict_do_nothing(
            index_elements=[user_roles_table.c.user_id, user_roles_table.c.role_id],
        ),
    )


def _insert_user_skills(connection: Connection) -> None:
    skill_values = sa.values(
        sa.column("username", sa.String(length=100)),
        sa.column("skill_name", sa.String(length=100)),
        name="mock_user_skills_values",
    ).data([(item["username"], item["skill_name"]) for item in USER_SKILLS])
    skill_select = sa.select(
        users_table.c.id.label("user_id"),
        skills_table.c.id.label("skill_id"),
    ).select_from(
        skill_values.join(
            users_table, users_table.c.username == skill_values.c.username,
        ).join(skills_table, skills_table.c.name == skill_values.c.skill_name),
    )
    connection.execute(
        pg_insert(user_skills_table)
        .from_select(
            [
                user_skills_table.c.user_id,
                user_skills_table.c.skill_id,
            ],
            skill_select,
        )
        .on_conflict_do_nothing(
            index_elements=[user_skills_table.c.user_id, user_skills_table.c.skill_id],
        ),
    )


def _insert_event_ratings(connection: Connection) -> None:
    ratings_values = sa.values(
        sa.column("event_title", sa.String(length=100)),
        sa.column("username", sa.String(length=100)),
        sa.column("status", sa.String(length=20)),
        sa.column("team_name", sa.String(length=100)),
        sa.column("awarded_at", sa.DateTime(timezone=True)),
        name="mock_event_ratings_values",
    ).data(
        [
            (
                item["event_title"],
                item["username"],
                item["status"],
                item["team_name"],
                item["awarded_at"],
            )
            for item in EVENT_RATINGS
        ],
    )
    ratings_select = sa.select(
        events_table.c.id.label("event_id"),
        users_table.c.id.label("user_id"),
        ratings_values.c.status,
        teams_table.c.id.label("team_id"),
        ratings_values.c.awarded_at,
    ).select_from(
        ratings_values.join(
            events_table, events_table.c.title == ratings_values.c.event_title,
        )
        .join(users_table, users_table.c.username == ratings_values.c.username)
        .outerjoin(teams_table, teams_table.c.name == ratings_values.c.team_name),
    )
    connection.execute(
        pg_insert(event_ratings_table)
        .from_select(
            [
                event_ratings_table.c.event_id,
                event_ratings_table.c.user_id,
                event_ratings_table.c.status,
                event_ratings_table.c.team_id,
                event_ratings_table.c.awarded_at,
            ],
            ratings_select,
        )
        .on_conflict_do_nothing(
            index_elements=[
                event_ratings_table.c.event_id,
                event_ratings_table.c.user_id,
            ],
        ),
    )


def _insert_telegram_identities(connection: Connection) -> None:
    identity_values = sa.values(
        sa.column("app_username", sa.String(length=100)),
        sa.column("telegram_user_id", sa.BigInteger()),
        sa.column("username", sa.String(length=100)),
        sa.column("first_name", sa.String(length=100)),
        sa.column("last_name", sa.String(length=100)),
        sa.column("photo_url", sa.String(length=2048)),
        sa.column("auth_date", sa.DateTime(timezone=True)),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        name="mock_telegram_identities_values",
    ).data(
        [
            (
                item["app_username"],
                item["telegram_user_id"],
                item["username"],
                item["first_name"],
                item["last_name"],
                item["photo_url"],
                item["auth_date"],
                item["created_at"],
                item["updated_at"],
            )
            for item in TELEGRAM_IDENTITIES
        ],
    )
    identity_select = sa.select(
        users_table.c.id.label("user_id"),
        identity_values.c.telegram_user_id,
        identity_values.c.username,
        identity_values.c.first_name,
        identity_values.c.last_name,
        identity_values.c.photo_url,
        identity_values.c.auth_date,
        identity_values.c.created_at,
        identity_values.c.updated_at,
    ).select_from(
        identity_values.join(
            users_table,
            users_table.c.username == identity_values.c.app_username,
        ),
    )
    connection.execute(
        pg_insert(telegram_identities_table)
        .from_select(
            [
                telegram_identities_table.c.user_id,
                telegram_identities_table.c.telegram_user_id,
                telegram_identities_table.c.username,
                telegram_identities_table.c.first_name,
                telegram_identities_table.c.last_name,
                telegram_identities_table.c.photo_url,
                telegram_identities_table.c.auth_date,
                telegram_identities_table.c.created_at,
                telegram_identities_table.c.updated_at,
            ],
            identity_select,
        )
        .on_conflict_do_nothing(),
    )


def upgrade() -> None:
    if not _is_mock_data_allowed():
        return

    connection = op.get_bind()
    connection.execute(
        pg_insert(roles_table)
        .values(list(ROLES))
        .on_conflict_do_nothing(index_elements=[roles_table.c.name]),
    )
    connection.execute(
        pg_insert(skills_table)
        .values(list(SKILLS))
        .on_conflict_do_nothing(index_elements=[skills_table.c.name]),
    )
    connection.execute(
        pg_insert(users_table).values(list(USERS)).on_conflict_do_nothing(),
    )
    connection.execute(
        pg_insert(teams_table)
        .values(list(TEAMS))
        .on_conflict_do_nothing(index_elements=[teams_table.c.name]),
    )
    _insert_events(connection)
    _insert_user_roles(connection)
    _insert_user_skills(connection)
    _insert_team_memberships(connection)
    _insert_telegram_identities(connection)
    _insert_event_ratings(connection)


def downgrade() -> None:
    if not _is_mock_data_allowed():
        return

    role_names = [row["name"] for row in ROLES]
    skill_names = [row["name"] for row in SKILLS]
    usernames = [row["username"] for row in USERS]
    team_names = [row["name"] for row in TEAMS]
    event_titles = [row["title"] for row in EVENTS]
    telegram_user_ids = [row["telegram_user_id"] for row in TELEGRAM_IDENTITIES]

    connection = op.get_bind()

    seeded_role_ids = sa.select(roles_table.c.id).where(
        roles_table.c.name.in_(role_names),
    )
    seeded_skill_ids = sa.select(skills_table.c.id).where(
        skills_table.c.name.in_(skill_names),
    )
    seeded_user_ids = sa.select(users_table.c.id).where(
        users_table.c.username.in_(usernames),
    )
    seeded_team_ids = sa.select(teams_table.c.id).where(
        teams_table.c.name.in_(team_names),
    )
    seeded_event_ids = sa.select(events_table.c.id).where(
        events_table.c.title.in_(event_titles),
    )

    connection.execute(
        sa.delete(event_ratings_table).where(
            sa.or_(
                event_ratings_table.c.event_id.in_(seeded_event_ids),
                event_ratings_table.c.user_id.in_(seeded_user_ids),
            ),
        ),
    )
    connection.execute(
        sa.delete(team_users_table).where(
            sa.or_(
                team_users_table.c.team_id.in_(seeded_team_ids),
                team_users_table.c.user_id.in_(seeded_user_ids),
            ),
        ),
    )
    connection.execute(
        sa.delete(user_roles_table).where(
            sa.or_(
                user_roles_table.c.user_id.in_(seeded_user_ids),
                user_roles_table.c.role_id.in_(seeded_role_ids),
            ),
        ),
    )
    connection.execute(
        sa.delete(user_skills_table).where(
            sa.or_(
                user_skills_table.c.user_id.in_(seeded_user_ids),
                user_skills_table.c.skill_id.in_(seeded_skill_ids),
            ),
        ),
    )
    connection.execute(
        sa.delete(telegram_identities_table).where(
            sa.or_(
                telegram_identities_table.c.user_id.in_(seeded_user_ids),
                telegram_identities_table.c.telegram_user_id.in_(telegram_user_ids),
            ),
        ),
    )
    connection.execute(
        sa.delete(events_table).where(events_table.c.title.in_(event_titles)),
    )
    connection.execute(sa.delete(teams_table).where(teams_table.c.name.in_(team_names)))
    connection.execute(
        sa.delete(users_table).where(users_table.c.username.in_(usernames)),
    )
    connection.execute(
        sa.delete(skills_table).where(skills_table.c.name.in_(skill_names)),
    )
    connection.execute(sa.delete(roles_table).where(roles_table.c.name.in_(role_names)))
