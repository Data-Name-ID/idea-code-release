from __future__ import annotations

from typing import TYPE_CHECKING, Self

from msgspec import Struct

from app.events.schemas import EventResponse
from app.users.schemas import UserShortResponse

if TYPE_CHECKING:
    from app.events.models import EventModel
    from app.teams.models import TeamModel


class TeamShortResponse(Struct, kw_only=True):
    id: int
    name: str
    description: str = ""

    @classmethod
    def from_model(cls, model: TeamModel) -> Self:
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
        )


class TeamResponse(Struct, kw_only=True):
    id: int
    name: str
    description: str = ""
    users: list[UserShortResponse] = []
    events: list[EventResponse] = []

    @classmethod
    def from_model(
        cls,
        model: TeamModel,
        *,
        events: list[EventModel],
    ) -> Self:
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            users=[UserShortResponse.from_model(user) for user in model.users],
            events=[EventResponse.from_model(event) for event in events],
        )


class TeamCreateRequest(Struct, kw_only=True):
    name: str
    description: str = ""
    user_ids: list[int] = []


class TeamUpdateRequest(Struct, kw_only=True):
    name: str | None = None
    description: str | None = None
    user_ids: list[int] | None = None
