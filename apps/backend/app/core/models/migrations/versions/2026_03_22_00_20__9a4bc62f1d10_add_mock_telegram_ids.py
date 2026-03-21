"""add mock telegram identities for local demo login

Revision ID: 9a4bc62f1d10
Revises: d8ed338de9b7
Create Date: 2026-03-22 00:20:00.000000
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "9a4bc62f1d10"
down_revision: str | None = "d8ed338de9b7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_MOCK_IDENTITIES: tuple[tuple[int, str, str], ...] = (
    (1677128852, "mock_tg_1677128852", "Mock TG 1677128852"),
    (1383319031, "mock_tg_1383319031", "Mock TG 1383319031"),
)
_MOCK_USER_ROLES: tuple[tuple[str, str], ...] = (
    ("mock_tg_1677128852", "mock_бэкенд"),
    ("mock_tg_1383319031", "mock_фронтенд"),
)
_MOCK_USER_SKILLS: tuple[tuple[str, str], ...] = (
    ("mock_tg_1677128852", "mock_python"),
    ("mock_tg_1383319031", "mock_vue"),
)


def _mock_seed_enabled() -> bool:
    return os.getenv("APP_MIGRATION_ALLOW_MOCK_DATA", "").strip().lower() == "true"


def _exec_sql(sql: str, params: dict[str, Any] | None = None) -> None:
    if params is None:
        op.execute(sa.text(sql))
        return
    op.get_bind().execute(sa.text(sql), params)


def _seed_users() -> None:
    for _, username, name in _MOCK_IDENTITIES:
        _exec_sql(
            """
                INSERT INTO users (
                    username,
                    email,
                    name,
                    avatar,
                    description,
                    location,
                    links,
                    password_hash,
                    activated,
                    created_at,
                    updated_at
                )
                VALUES (
                    :username,
                    NULL,
                    :name,
                    NULL,
                    'Mock user for Telegram auth smoke checks.',
                    '',
                    '[]'::jsonb,
                    NULL,
                    true,
                    timezone('utc', now()),
                    timezone('utc', now())
                )
                ON CONFLICT (username) DO NOTHING
            """,
            {"username": username, "name": name},
        )


def _seed_telegram_identities() -> None:
    for tg_id, username, name in _MOCK_IDENTITIES:
        _exec_sql(
            """
                INSERT INTO telegram_identities (
                    user_id,
                    telegram_user_id,
                    username,
                    first_name,
                    last_name,
                    photo_url,
                    auth_date,
                    created_at,
                    updated_at
                )
                SELECT
                    users.id,
                    :tg_id,
                    :username,
                    :name,
                    NULL,
                    NULL,
                    timezone('utc', now()),
                    timezone('utc', now()),
                    timezone('utc', now())
                FROM users
                WHERE users.username = :username
                ON CONFLICT (telegram_user_id) DO UPDATE
                SET
                    user_id = excluded.user_id,
                    username = excluded.username,
                    first_name = excluded.first_name,
                    last_name = excluded.last_name,
                    photo_url = excluded.photo_url,
                    auth_date = excluded.auth_date,
                    updated_at = timezone('utc', now())
            """,
            {"tg_id": tg_id, "username": username, "name": name},
        )


def _seed_user_roles() -> None:
    _exec_sql(
        """
            WITH relation(username, role_name) AS (
                VALUES
                    ('mock_tg_1677128852', 'mock_бэкенд'),
                    ('mock_tg_1383319031', 'mock_фронтенд')
            )
            INSERT INTO user_roles (user_id, role_id)
            SELECT users.id, roles.id
            FROM relation
            JOIN users ON users.username = relation.username
            JOIN roles ON roles.name = relation.role_name
            ON CONFLICT DO NOTHING
        """,
    )


def _seed_user_skills() -> None:
    _exec_sql(
        """
            WITH relation(username, skill_name) AS (
                VALUES
                    ('mock_tg_1677128852', 'mock_python'),
                    ('mock_tg_1383319031', 'mock_vue')
            )
            INSERT INTO user_skills (user_id, skill_id)
            SELECT users.id, skills.id
            FROM relation
            JOIN users ON users.username = relation.username
            JOIN skills ON skills.name = relation.skill_name
            ON CONFLICT DO NOTHING
        """,
    )


def upgrade() -> None:
    if not _mock_seed_enabled():
        return

    _seed_users()
    _seed_telegram_identities()
    _seed_user_roles()
    _seed_user_skills()


def downgrade() -> None:
    if not _mock_seed_enabled():
        return

    _exec_sql(
        """
            DELETE FROM user_roles
            WHERE user_id IN (
                SELECT id FROM users WHERE username = ANY(:usernames)
            )
        """,
        {"usernames": [username for _, username, _ in _MOCK_IDENTITIES]},
    )
    _exec_sql(
        """
            DELETE FROM user_skills
            WHERE user_id IN (
                SELECT id FROM users WHERE username = ANY(:usernames)
            )
        """,
        {"usernames": [username for _, username, _ in _MOCK_IDENTITIES]},
    )
    _exec_sql(
        """
            DELETE FROM telegram_identities
            WHERE telegram_user_id = ANY(:tg_ids)
        """,
        {"tg_ids": [tg_id for tg_id, _, _ in _MOCK_IDENTITIES]},
    )
    _exec_sql(
        """
            DELETE FROM users
            WHERE username = ANY(:usernames)
        """,
        {"usernames": [username for _, username, _ in _MOCK_IDENTITIES]},
    )
