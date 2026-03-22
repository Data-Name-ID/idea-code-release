from __future__ import annotations

from datetime import datetime  # noqa: TC003
from enum import StrEnum
from typing import TYPE_CHECKING, Self

from msgspec import Struct

if TYPE_CHECKING:
    from app.events.models import EventModel, EventRatingModel


class EventRatingStatus(StrEnum):
    WINNER = "winner"
    PRIZE_WINNER = "prize_winner"
    PARTICIPANT = "participant"


class EventResponse(Struct, kw_only=True):
    id: int
    title: str
    description: str = ""
    date: datetime
    cover: str | None = None
    is_verify: bool = False

    @classmethod
    def from_model(cls, model: EventModel) -> Self:
        return cls(
            id=model.id,
            title=model.title,
            description=model.description,
            date=model.date,
            cover=model.cover,
            is_verify=model.is_verify,
        )


class EventListResponse(Struct, kw_only=True):
    total: int
    limit: int
    offset: int
    data: list[EventResponse]


class EventCreateRequest(Struct, kw_only=True):
    title: str
    description: str = ""
    date: datetime
    cover: str | None = None
    is_verify: bool = False


class EventUpdateRequest(Struct, kw_only=True):
    title: str | None = None
    description: str | None = None
    date: datetime | None = None
    cover: str | None = None
    is_verify: bool | None = None


class EventRatingEntryResponse(Struct, kw_only=True):
    user_id: int
    status: EventRatingStatus
    team_id: int | None = None
    awarded_at: datetime | None = None

    @classmethod
    def from_model(cls, model: EventRatingModel) -> Self:
        return cls(
            user_id=model.user_id,
            status=EventRatingStatus(model.status),
            team_id=model.team_id,
            awarded_at=model.awarded_at,
        )


class EventRatingResponse(Struct, kw_only=True):
    event_id: int
    ratings: list[EventRatingEntryResponse]


class EventRatingCreateRequest(Struct, kw_only=True):
    user_id: int
    status: EventRatingStatus
    team_id: int | None = None
