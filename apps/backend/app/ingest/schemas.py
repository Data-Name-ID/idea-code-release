from __future__ import annotations

from datetime import datetime  # noqa: TC003

from msgspec import Struct

from app.events.schemas import EventRatingStatus  # noqa: TC001


class OrganizerMemberInput(Struct, kw_only=True):
    telegram_id: int | None = None
    email: str | None = None
    username: str | None = None
    name: str = ""
    avatar: str | None = None


class OrganizerHackathonInput(Struct, kw_only=True):
    external_id: str
    title: str
    description: str = ""
    date: datetime
    cover: str | None = None


class OrganizerTeamInput(Struct, kw_only=True):
    external_id: str
    name: str
    description: str = ""
    members: list[OrganizerMemberInput] = []


class OrganizerResultInput(Struct, kw_only=True):
    status: EventRatingStatus | None = None
    place: int | None = None
    awarded_at: datetime | None = None
    team_external_id: str | None = None
    user: OrganizerMemberInput | None = None


class OrganizerImportRequest(Struct, kw_only=True):
    hackathon: OrganizerHackathonInput
    teams: list[OrganizerTeamInput] = []
    results: list[OrganizerResultInput] = []


class OrganizerImportCounters(Struct, kw_only=True):
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0


class OrganizerImportError(Struct, kw_only=True):
    entity: str
    key: str
    detail: str


class OrganizerImportResponse(Struct, kw_only=True):
    hackathons: OrganizerImportCounters
    teams: OrganizerImportCounters
    results: OrganizerImportCounters
    errors: list[OrganizerImportError] = []
