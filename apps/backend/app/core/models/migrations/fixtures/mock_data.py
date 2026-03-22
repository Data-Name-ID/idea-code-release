from __future__ import annotations

from datetime import UTC, datetime
from typing import Final, TypedDict


class LinkFixture(TypedDict):
    url: str
    label: str


class RoleFixture(TypedDict):
    name: str


class SkillFixture(TypedDict):
    name: str


class UserFixture(TypedDict):
    username: str
    email: str
    name: str
    avatar: str | None
    description: str
    location: str
    links: list[LinkFixture]
    activated: bool
    created_at: datetime
    updated_at: datetime


class TeamFixture(TypedDict):
    name: str
    description: str
    created_at: datetime
    updated_at: datetime


class TeamMembershipFixture(TypedDict):
    team_name: str
    username: str


class UserRoleFixture(TypedDict):
    username: str
    role_name: str


class UserSkillFixture(TypedDict):
    username: str
    skill_name: str


class EventFixture(TypedDict):
    title: str
    description: str
    date: datetime
    cover: str | None
    is_verify: bool
    created_at: datetime
    updated_at: datetime


class EventRatingFixture(TypedDict):
    event_title: str
    username: str
    status: str
    team_name: str | None
    awarded_at: datetime


class TelegramIdentityFixture(TypedDict):
    app_username: str
    telegram_user_id: int
    username: str | None
    first_name: str
    last_name: str | None
    photo_url: str | None
    auth_date: datetime
    created_at: datetime
    updated_at: datetime


SEED_CREATED_AT: Final = datetime(2026, 3, 22, 12, 0, tzinfo=UTC)

ROLES: Final[tuple[RoleFixture, ...]] = (
    {"name": "mock_admin"},
    {"name": "mock_mentor"},
    {"name": "mock_participant"},
)

SKILLS: Final[tuple[SkillFixture, ...]] = (
    {"name": "mock_python"},
    {"name": "mock_vue"},
    {"name": "mock_postgresql"},
    {"name": "mock_uiux"},
)

USERS: Final[tuple[UserFixture, ...]] = (
    {
        "username": "mock_alice",
        "email": "mock.alice@example.test",
        "name": "Alice Mock",
        "avatar": "https://example.test/mock/alice.png",
        "description": "Backend mentor for demo environment.",
        "location": "Moscow",
        "links": [
            {"url": "https://github.com/mock-alice", "label": "GitHub"},
            {"url": "https://t.me/mock_alice", "label": "Telegram"},
        ],
        "activated": True,
        "created_at": SEED_CREATED_AT,
        "updated_at": SEED_CREATED_AT,
    },
    {
        "username": "mock_bob",
        "email": "mock.bob@example.test",
        "name": "Bob Mock",
        "avatar": "https://example.test/mock/bob.png",
        "description": "Frontend participant for demo environment.",
        "location": "Kazan",
        "links": [
            {"url": "https://github.com/mock-bob", "label": "GitHub"},
        ],
        "activated": True,
        "created_at": SEED_CREATED_AT,
        "updated_at": SEED_CREATED_AT,
    },
    {
        "username": "mock_carol",
        "email": "mock.carol@example.test",
        "name": "Carol Mock",
        "avatar": "https://example.test/mock/carol.png",
        "description": "Design lead for demo environment.",
        "location": "Saint Petersburg",
        "links": [
            {"url": "https://instagram.com/mock_carol", "label": "Instagram"},
        ],
        "activated": True,
        "created_at": SEED_CREATED_AT,
        "updated_at": SEED_CREATED_AT,
    },
)

TEAMS: Final[tuple[TeamFixture, ...]] = (
    {
        "name": "mock_team_core",
        "description": "Core product team loaded by migration fixture.",
        "created_at": SEED_CREATED_AT,
        "updated_at": SEED_CREATED_AT,
    },
    {
        "name": "mock_team_design",
        "description": "Design team loaded by migration fixture.",
        "created_at": SEED_CREATED_AT,
        "updated_at": SEED_CREATED_AT,
    },
)

TEAM_MEMBERSHIPS: Final[tuple[TeamMembershipFixture, ...]] = (
    {"team_name": "mock_team_core", "username": "mock_alice"},
    {"team_name": "mock_team_core", "username": "mock_bob"},
    {"team_name": "mock_team_design", "username": "mock_carol"},
)

USER_ROLES: Final[tuple[UserRoleFixture, ...]] = (
    {"username": "mock_alice", "role_name": "mock_admin"},
    {"username": "mock_bob", "role_name": "mock_participant"},
    {"username": "mock_carol", "role_name": "mock_mentor"},
)

USER_SKILLS: Final[tuple[UserSkillFixture, ...]] = (
    {"username": "mock_alice", "skill_name": "mock_python"},
    {"username": "mock_alice", "skill_name": "mock_postgresql"},
    {"username": "mock_bob", "skill_name": "mock_vue"},
    {"username": "mock_carol", "skill_name": "mock_uiux"},
)

EVENTS: Final[tuple[EventFixture, ...]] = (
    {
        "title": "__mock_seed__backend_hackathon_2026",
        "description": "Backend demo event inserted by migration fixture.",
        "date": datetime(2026, 4, 12, 10, 0, tzinfo=UTC),
        "cover": "https://example.test/mock/events/backend-hackathon.png",
        "is_verify": True,
        "created_at": SEED_CREATED_AT,
        "updated_at": SEED_CREATED_AT,
    },
    {
        "title": "__mock_seed__frontend_showcase_2026",
        "description": "Frontend demo event inserted by migration fixture.",
        "date": datetime(2026, 5, 16, 12, 30, tzinfo=UTC),
        "cover": "https://example.test/mock/events/frontend-showcase.png",
        "is_verify": False,
        "created_at": SEED_CREATED_AT,
        "updated_at": SEED_CREATED_AT,
    },
)

EVENT_RATINGS: Final[tuple[EventRatingFixture, ...]] = (
    {
        "event_title": "__mock_seed__backend_hackathon_2026",
        "username": "mock_alice",
        "status": "winner",
        "team_name": "mock_team_core",
        "awarded_at": datetime(2026, 4, 12, 17, 0, tzinfo=UTC),
    },
    {
        "event_title": "__mock_seed__backend_hackathon_2026",
        "username": "mock_bob",
        "status": "participant",
        "team_name": "mock_team_core",
        "awarded_at": datetime(2026, 4, 12, 17, 0, tzinfo=UTC),
    },
    {
        "event_title": "__mock_seed__frontend_showcase_2026",
        "username": "mock_carol",
        "status": "prize_winner",
        "team_name": "mock_team_design",
        "awarded_at": datetime(2026, 5, 16, 18, 0, tzinfo=UTC),
    },
)

TELEGRAM_IDENTITIES: Final[tuple[TelegramIdentityFixture, ...]] = (
    {
        "app_username": "mock_alice",
        "telegram_user_id": 9800000001,
        "username": "mock_alice_tg",
        "first_name": "Alice",
        "last_name": "Mock",
        "photo_url": "https://example.test/mock/tg/alice.png",
        "auth_date": SEED_CREATED_AT,
        "created_at": SEED_CREATED_AT,
        "updated_at": SEED_CREATED_AT,
    },
    {
        "app_username": "mock_bob",
        "telegram_user_id": 9800000002,
        "username": "mock_bob_tg",
        "first_name": "Bob",
        "last_name": "Mock",
        "photo_url": "https://example.test/mock/tg/bob.png",
        "auth_date": SEED_CREATED_AT,
        "created_at": SEED_CREATED_AT,
        "updated_at": SEED_CREATED_AT,
    },
)
