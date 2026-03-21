"""seed mock data for empty telegram user profiles

Revision ID: a1b2c3d4e5f6
Revises: c2d3e4f5a6b7
Create Date: 2026-03-22 00:45:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "c2d3e4f5a6b7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            WITH mock_profiles AS (
                SELECT *
                FROM (
                    VALUES
                        (
                            1383319031::bigint,
                            'Mock User 1383319031',
                            'Mock profile for Telegram user 1383319031',
                            'Moscow',
                            'https://i.pravatar.cc/300?img=12',
                            '[{"label":"GitHub","url":"https://github.com/mock-1383319031"},{"label":"Website","url":"https://mock-1383319031.local"}]'::jsonb
                        ),
                        (
                            1677128852::bigint,
                            'Mock User 1677128852',
                            'Mock profile for Telegram user 1677128852',
                            'Saint Petersburg',
                            'https://i.pravatar.cc/300?img=32',
                            '[{"label":"GitHub","url":"https://github.com/mock-1677128852"},{"label":"Website","url":"https://mock-1677128852.local"}]'::jsonb
                        )
                ) AS v(
                    telegram_user_id,
                    name,
                    description,
                    location,
                    avatar,
                    links
                )
            )
            UPDATE users AS u
            SET
                name = CASE WHEN u.name = '' THEN mp.name ELSE u.name END,
                description = CASE
                    WHEN u.description = '' THEN mp.description
                    ELSE u.description
                END,
                location = CASE
                    WHEN u.location = '' THEN mp.location
                    ELSE u.location
                END,
                avatar = COALESCE(u.avatar, mp.avatar),
                links = CASE
                    WHEN jsonb_array_length(u.links) = 0 THEN mp.links
                    ELSE u.links
                END,
                activated = TRUE
            FROM telegram_identities AS ti
            JOIN mock_profiles AS mp
                ON mp.telegram_user_id = ti.telegram_user_id
            WHERE u.id = ti.user_id
            """,
        ),
    )

    op.execute(
        sa.text(
            """
            WITH mock_identities AS (
                SELECT *
                FROM (
                    VALUES
                        (
                            1383319031::bigint,
                            'mock_1383319031',
                            'Mock',
                            'One',
                            'https://i.pravatar.cc/300?img=12'
                        ),
                        (
                            1677128852::bigint,
                            'mock_1677128852',
                            'Mock',
                            'Two',
                            'https://i.pravatar.cc/300?img=32'
                        )
                ) AS v(
                    telegram_user_id,
                    username,
                    first_name,
                    last_name,
                    photo_url
                )
            )
            UPDATE telegram_identities AS ti
            SET
                username = COALESCE(NULLIF(ti.username, ''), mi.username),
                first_name = CASE
                    WHEN ti.first_name = '' THEN mi.first_name
                    ELSE ti.first_name
                END,
                last_name = COALESCE(ti.last_name, mi.last_name),
                photo_url = COALESCE(ti.photo_url, mi.photo_url)
            FROM mock_identities AS mi
            WHERE ti.telegram_user_id = mi.telegram_user_id
            """,
        ),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO roles (name)
            VALUES
                ('mock-role-1383319031'),
                ('mock-role-1677128852')
            ON CONFLICT (name) DO NOTHING
            """,
        ),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO skills (name)
            VALUES
                ('mock-skill-1383319031'),
                ('mock-skill-1677128852')
            ON CONFLICT (name) DO NOTHING
            """,
        ),
    )

    op.execute(
        sa.text(
            """
            WITH target_users AS (
                SELECT ti.user_id, ti.telegram_user_id
                FROM telegram_identities AS ti
                WHERE ti.telegram_user_id IN (1383319031, 1677128852)
            ),
            role_mapping AS (
                SELECT *
                FROM (
                    VALUES
                        (1383319031::bigint, 'mock-role-1383319031'),
                        (1677128852::bigint, 'mock-role-1677128852')
                ) AS v(telegram_user_id, role_name)
            )
            INSERT INTO user_roles (user_id, role_id)
            SELECT tu.user_id, r.id
            FROM role_mapping AS rm
            JOIN target_users AS tu
                ON tu.telegram_user_id = rm.telegram_user_id
            JOIN roles AS r
                ON r.name = rm.role_name
            ON CONFLICT (user_id, role_id) DO NOTHING
            """,
        ),
    )

    op.execute(
        sa.text(
            """
            WITH target_users AS (
                SELECT ti.user_id, ti.telegram_user_id
                FROM telegram_identities AS ti
                WHERE ti.telegram_user_id IN (1383319031, 1677128852)
            ),
            skill_mapping AS (
                SELECT *
                FROM (
                    VALUES
                        (1383319031::bigint, 'mock-skill-1383319031'),
                        (1677128852::bigint, 'mock-skill-1677128852')
                ) AS v(telegram_user_id, skill_name)
            )
            INSERT INTO user_skills (user_id, skill_id)
            SELECT tu.user_id, s.id
            FROM skill_mapping AS sm
            JOIN target_users AS tu
                ON tu.telegram_user_id = sm.telegram_user_id
            JOIN skills AS s
                ON s.name = sm.skill_name
            ON CONFLICT (user_id, skill_id) DO NOTHING
            """,
        ),
    )

    op.execute(
        sa.text(
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
                    'mock-event-1383319031',
                    'Mock event for Telegram user 1383319031',
                    timezone('utc', now()) + interval '7 days',
                    'https://images.unsplash.com/photo-1521737711867-e3b97375f902',
                    TRUE,
                    timezone('utc', now()),
                    timezone('utc', now())
                ),
                (
                    'mock-event-1677128852',
                    'Mock event for Telegram user 1677128852',
                    timezone('utc', now()) + interval '14 days',
                    'https://images.unsplash.com/photo-1515169067865-5387ec356754',
                    TRUE,
                    timezone('utc', now()),
                    timezone('utc', now())
                )
            """,
        ),
    )

    op.execute(
        sa.text(
            """
            WITH target_users AS (
                SELECT ti.user_id, ti.telegram_user_id
                FROM telegram_identities AS ti
                WHERE ti.telegram_user_id IN (1383319031, 1677128852)
            ),
            rating_mapping AS (
                SELECT *
                FROM (
                    VALUES
                        ('mock-event-1383319031', 1383319031::bigint, 'owner', 1),
                        ('mock-event-1677128852', 1677128852::bigint, 'owner', 2)
                ) AS v(event_title, telegram_user_id, status, team_id)
            )
            INSERT INTO event_ratings (event_id, user_id, status, team_id, awarded_at)
            SELECT e.id, tu.user_id, rm.status, rm.team_id, timezone('utc', now())
            FROM rating_mapping AS rm
            JOIN events AS e
                ON e.title = rm.event_title
            JOIN target_users AS tu
                ON tu.telegram_user_id = rm.telegram_user_id
            ON CONFLICT (event_id, user_id)
            DO UPDATE SET
                status = EXCLUDED.status,
                team_id = EXCLUDED.team_id,
                awarded_at = EXCLUDED.awarded_at
            """,
        ),
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DELETE FROM event_ratings AS er
            USING events AS e, telegram_identities AS ti
            WHERE er.event_id = e.id
              AND er.user_id = ti.user_id
              AND e.title IN ('mock-event-1383319031', 'mock-event-1677128852')
              AND ti.telegram_user_id IN (1383319031, 1677128852)
            """,
        ),
    )

    op.execute(
        sa.text(
            """
            DELETE FROM events
            WHERE title IN ('mock-event-1383319031', 'mock-event-1677128852')
            """,
        ),
    )

    op.execute(
        sa.text(
            """
            DELETE FROM user_roles AS ur
            USING roles AS r, telegram_identities AS ti
            WHERE ur.role_id = r.id
              AND ur.user_id = ti.user_id
              AND r.name IN ('mock-role-1383319031', 'mock-role-1677128852')
              AND ti.telegram_user_id IN (1383319031, 1677128852)
            """,
        ),
    )

    op.execute(
        sa.text(
            """
            DELETE FROM user_skills AS us
            USING skills AS s, telegram_identities AS ti
            WHERE us.skill_id = s.id
              AND us.user_id = ti.user_id
              AND s.name IN ('mock-skill-1383319031', 'mock-skill-1677128852')
              AND ti.telegram_user_id IN (1383319031, 1677128852)
            """,
        ),
    )

    op.execute(
        sa.text(
            """
            DELETE FROM roles AS r
            WHERE r.name IN ('mock-role-1383319031', 'mock-role-1677128852')
              AND NOT EXISTS (
                SELECT 1
                FROM user_roles AS ur
                WHERE ur.role_id = r.id
              )
            """,
        ),
    )

    op.execute(
        sa.text(
            """
            DELETE FROM skills AS s
            WHERE s.name IN ('mock-skill-1383319031', 'mock-skill-1677128852')
              AND NOT EXISTS (
                SELECT 1
                FROM user_skills AS us
                WHERE us.skill_id = s.id
              )
            """,
        ),
    )
