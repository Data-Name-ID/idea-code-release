"""seed mock demo data

Revision ID: d8ed338de9b7
Revises: c2d3e4f5a6b7
Create Date: 2026-03-21 23:40:38.331408
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "d8ed338de9b7"
down_revision: str | None = "c2d3e4f5a6b7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_MOCK_USERNAMES = (
    "mock_alex_dev",
    "mock_nina_design",
    "mock_igor_pm",
    "mock_maria_qa",
)
_MOCK_ROLE_NAMES = (
    "mock_бэкенд",
    "mock_фронтенд",
    "mock_дизайнер",
    "mock_продакт",
)
_MOCK_SKILL_NAMES = (
    "mock_python",
    "mock_vue",
    "mock_figma",
    "mock_postgresql",
    "mock_тестирование",
    "mock_продуктовая_аналитика",
)
_MOCK_EVENT_TITLES = (
    "Мок Демо: Старт продуктового спринта",
    "Мок Демо: Встреча фронтенд-гильдии",
    "Мок Демо: Лаборатория QA-паринга",
)


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
                ('mock_фронтенд'),
                ('mock_дизайнер'),
                ('mock_продакт')
            ON CONFLICT (name) DO NOTHING
        """,
    )


def _seed_skills() -> None:
    _exec_sql(
        """
            INSERT INTO skills (name)
            VALUES
                ('mock_python'),
                ('mock_vue'),
                ('mock_figma'),
                ('mock_postgresql'),
                ('mock_тестирование'),
                ('mock_продуктовая_аналитика')
            ON CONFLICT (name) DO NOTHING
        """,
    )


def _seed_users() -> None:
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
            VALUES
                (
                    'mock_alex_dev',
                    'mock.alex@example.com',
                    'Алексей Разработчик',
                    'https://example.com/avatars/alex.png',
                    'Бэкенд-инженер для демонстрационных данных.',
                    'Москва',
                    '[{"url":"https://github.com/mock-alex","label":"Гитхаб"}]'::jsonb,
                    NULL,
                    true,
                    timezone('utc', now()),
                    timezone('utc', now())
                ),
                (
                    'mock_nina_design',
                    'mock.nina@example.com',
                    'Нина Дизайнер',
                    'https://example.com/avatars/nina.png',
                    'Продуктовый дизайнер для демонстрационных данных.',
                    'Санкт-Петербург',
                    '[{"url":"https://dribbble.com/mock-nina","label":"Портфолио"}]'::jsonb,
                    NULL,
                    true,
                    timezone('utc', now()),
                    timezone('utc', now())
                ),
                (
                    'mock_igor_pm',
                    'mock.igor@example.com',
                    'Игорь Продакт',
                    'https://example.com/avatars/igor.png',
                    'Продакт-менеджер для демонстрационных данных.',
                    'Казань',
                    '[{"url":"https://t.me/mock_igor","label":"Телеграм"}]'::jsonb,
                    NULL,
                    true,
                    timezone('utc', now()),
                    timezone('utc', now())
                ),
                (
                    'mock_maria_qa',
                    'mock.maria@example.com',
                    'Мария QA',
                    'https://example.com/avatars/maria.png',
                    'QA-инженер для демонстрационных данных.',
                    'Екатеринбург',
                    '[{"url":"https://x.com/mock_maria","label":"X"}]'::jsonb,
                    NULL,
                    true,
                    timezone('utc', now()),
                    timezone('utc', now())
                )
            ON CONFLICT (username) DO NOTHING
        """,
    )


def _seed_user_roles() -> None:
    _exec_sql(
        """
            WITH relation(username, role_name) AS (
                VALUES
                    ('mock_alex_dev', 'mock_бэкенд'),
                    ('mock_alex_dev', 'mock_фронтенд'),
                    ('mock_nina_design', 'mock_дизайнер'),
                    ('mock_igor_pm', 'mock_продакт'),
                    ('mock_maria_qa', 'mock_бэкенд')
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
                    ('mock_alex_dev', 'mock_python'),
                    ('mock_alex_dev', 'mock_postgresql'),
                    ('mock_nina_design', 'mock_figma'),
                    ('mock_nina_design', 'mock_vue'),
                    ('mock_igor_pm', 'mock_продуктовая_аналитика'),
                    ('mock_maria_qa', 'mock_тестирование')
            )
            INSERT INTO user_skills (user_id, skill_id)
            SELECT users.id, skills.id
            FROM relation
            JOIN users ON users.username = relation.username
            JOIN skills ON skills.name = relation.skill_name
            ON CONFLICT DO NOTHING
        """,
    )


def _seed_events() -> None:
    _exec_sql(
        """
            INSERT INTO events (
                title,
                description,
                date,
                cover,
                is_verify,
                created_at,
                updated_at
            )
            VALUES
                (
                    'Мок Демо: Старт продуктового спринта',
                    'Демо-событие для планирования и распределения ролей.',
                    timezone('utc', now()) + interval '7 days',
                    'https://example.com/covers/kickoff.png',
                    true,
                    timezone('utc', now()),
                    timezone('utc', now())
                ),
                (
                    'Мок Демо: Встреча фронтенд-гильдии',
                    'Демо-событие по практикам фронтенд-взаимодействия.',
                    timezone('utc', now()) + interval '14 days',
                    'https://example.com/covers/frontend.png',
                    false,
                    timezone('utc', now()),
                    timezone('utc', now())
                ),
                (
                    'Мок Демо: Лаборатория QA-паринга',
                    'Демо-событие по тест-стратегии и парной работе.',
                    timezone('utc', now()) + interval '21 days',
                    'https://example.com/covers/qa.png',
                    false,
                    timezone('utc', now()),
                    timezone('utc', now())
                )
        """,
    )


def _seed_event_ratings() -> None:
    _exec_sql(
        """
            WITH relation(event_title, username, status, team_id) AS (
                VALUES
                    (
                        'Мок Демо: Старт продуктового спринта',
                        'mock_alex_dev',
                        'одобрено',
                        1
                    ),
                    (
                        'Мок Демо: Старт продуктового спринта',
                        'mock_igor_pm',
                        'одобрено',
                        1
                    ),
                    (
                        'Мок Демо: Встреча фронтенд-гильдии',
                        'mock_nina_design',
                        'в_ожидании',
                        2
                    ),
                    (
                        'Мок Демо: Встреча фронтенд-гильдии',
                        'mock_alex_dev',
                        'одобрено',
                        2
                    ),
                    (
                        'Мок Демо: Лаборатория QA-паринга',
                        'mock_maria_qa',
                        'одобрено',
                        3
                    )
            )
            INSERT INTO event_ratings (event_id, user_id, status, team_id, awarded_at)
            SELECT
                events.id,
                users.id,
                relation.status,
                relation.team_id,
                timezone('utc', now())
            FROM relation
            JOIN events ON events.title = relation.event_title
            JOIN users ON users.username = relation.username
            ON CONFLICT (event_id, user_id) DO UPDATE
            SET
                status = EXCLUDED.status,
                team_id = EXCLUDED.team_id,
                awarded_at = EXCLUDED.awarded_at
        """,
    )


def upgrade() -> None:
    if not _mock_seed_enabled():
        return

    _seed_roles()
    _seed_skills()
    _seed_users()
    _seed_user_roles()
    _seed_user_skills()
    _seed_events()
    _seed_event_ratings()


def downgrade() -> None:
    if not _mock_seed_enabled():
        return

    _exec_sql(
        """
            DELETE FROM event_ratings
            WHERE event_id IN (
                SELECT id FROM events WHERE title = ANY(:titles)
            )
            OR user_id IN (
                SELECT id FROM users WHERE username = ANY(:usernames)
            )
        """,
        {
            "titles": list(_MOCK_EVENT_TITLES),
            "usernames": list(_MOCK_USERNAMES),
        },
    )

    _exec_sql(
        """
        DELETE FROM user_roles
        WHERE user_id IN (SELECT id FROM users WHERE username = ANY(:usernames))
        """,
        {"usernames": list(_MOCK_USERNAMES)},
    )

    _exec_sql(
        """
        DELETE FROM user_skills
        WHERE user_id IN (SELECT id FROM users WHERE username = ANY(:usernames))
        """,
        {"usernames": list(_MOCK_USERNAMES)},
    )

    _exec_sql(
        "DELETE FROM events WHERE title = ANY(:titles)",
        {"titles": list(_MOCK_EVENT_TITLES)},
    )

    _exec_sql(
        "DELETE FROM users WHERE username = ANY(:usernames)",
        {"usernames": list(_MOCK_USERNAMES)},
    )

    _exec_sql(
        "DELETE FROM roles WHERE name = ANY(:names)",
        {"names": list(_MOCK_ROLE_NAMES)},
    )

    _exec_sql(
        "DELETE FROM skills WHERE name = ANY(:names)",
        {"names": list(_MOCK_SKILL_NAMES)},
    )
