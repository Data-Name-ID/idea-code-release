"""backfill mock profile data for existing telegram users

Revision ID: 7c1f9e8a4d2b
Revises: 9a4bc62f1d10
Create Date: 2026-03-22 00:45:00.000000
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "7c1f9e8a4d2b"
down_revision: str | None = "9a4bc62f1d10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_MOCK_TG_IDS: tuple[int, ...] = (1677128852, 1383319031)


def _mock_seed_enabled() -> bool:
    return os.getenv("APP_MIGRATION_ALLOW_MOCK_DATA", "").strip().lower() == "true"


def _exec_sql(sql: str, params: dict[str, Any] | None = None) -> None:
    if params is None:
        op.execute(sa.text(sql))
        return
    op.get_bind().execute(sa.text(sql), params)


def _seed_roles() -> None:
    _exec_sql(
        """
            INSERT INTO roles (name)
            VALUES
                ('mock_бэкенд'),
                ('mock_фронтенд')
            ON CONFLICT (name) DO NOTHING
        """,
    )


def _seed_skills() -> None:
    _exec_sql(
        """
            INSERT INTO skills (name)
            VALUES
                ('mock_python'),
                ('mock_vue')
            ON CONFLICT (name) DO NOTHING
        """,
    )


def _backfill_users() -> None:
    _exec_sql(
        """
            WITH mock_data(tg_id, username, name, description, location, links) AS (
                VALUES
                    (
                        1677128852,
                        'mock_tg_1677128852',
                        'Mock TG 1677128852',
                        'Mock user for Telegram auth smoke checks.',
                        '',
                        '[{"url":"https://t.me/mock_tg_1677128852","label":"Telegram"}]'::jsonb
                    ),
                    (
                        1383319031,
                        'mock_tg_1383319031',
                        'Mock TG 1383319031',
                        'Mock user for Telegram auth smoke checks.',
                        '',
                        '[{"url":"https://t.me/mock_tg_1383319031","label":"Telegram"}]'::jsonb
                    )
            )
            UPDATE users
            SET
                username = CASE
                    WHEN users.username = '' THEN mock_data.username
                    ELSE users.username
                END,
                name = mock_data.name,
                description = mock_data.description,
                location = mock_data.location,
                links = mock_data.links,
                activated = true,
                updated_at = timezone('utc', now())
            FROM telegram_identities
            JOIN mock_data ON mock_data.tg_id = telegram_identities.telegram_user_id
            WHERE users.id = telegram_identities.user_id
        """,
    )


def _seed_user_roles() -> None:
    _exec_sql(
        """
            WITH relation(tg_id, role_name) AS (
                VALUES
                    (1677128852, 'mock_бэкенд'),
                    (1383319031, 'mock_фронтенд')
            )
            INSERT INTO user_roles (user_id, role_id)
            SELECT telegram_identities.user_id, roles.id
            FROM relation
            JOIN telegram_identities
                ON telegram_identities.telegram_user_id = relation.tg_id
            JOIN roles ON roles.name = relation.role_name
            ON CONFLICT DO NOTHING
        """,
    )


def _seed_user_skills() -> None:
    _exec_sql(
        """
            WITH relation(tg_id, skill_name) AS (
                VALUES
                    (1677128852, 'mock_python'),
                    (1383319031, 'mock_vue')
            )
            INSERT INTO user_skills (user_id, skill_id)
            SELECT telegram_identities.user_id, skills.id
            FROM relation
            JOIN telegram_identities
                ON telegram_identities.telegram_user_id = relation.tg_id
            JOIN skills ON skills.name = relation.skill_name
            ON CONFLICT DO NOTHING
        """,
    )


def upgrade() -> None:
    if not _mock_seed_enabled():
        return

    _seed_roles()
    _seed_skills()
    _backfill_users()
    _seed_user_roles()
    _seed_user_skills()


def downgrade() -> None:
    if not _mock_seed_enabled():
        return

    _exec_sql(
        """
            DELETE FROM user_roles
            WHERE role_id IN (
                SELECT id FROM roles WHERE name IN ('mock_бэкенд', 'mock_фронтенд')
            )
            AND user_id IN (
                SELECT user_id
                FROM telegram_identities
                WHERE telegram_user_id = ANY(:tg_ids)
            )
        """,
        {"tg_ids": list(_MOCK_TG_IDS)},
    )
    _exec_sql(
        """
            DELETE FROM user_skills
            WHERE skill_id IN (
                SELECT id FROM skills WHERE name IN ('mock_python', 'mock_vue')
            )
            AND user_id IN (
                SELECT user_id
                FROM telegram_identities
                WHERE telegram_user_id = ANY(:tg_ids)
            )
        """,
        {"tg_ids": list(_MOCK_TG_IDS)},
    )
