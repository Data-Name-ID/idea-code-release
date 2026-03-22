from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING, Self

from msgspec import Struct

from app.events.schemas import EventResponse
from app.users.schemas import LinkRequest, LinkResponse, UserShortResponse

if TYPE_CHECKING:
    from app.events.models import EventModel
    from app.teams.models import TeamInviteModel, TeamModel
    from app.users.domain import LinkData


class TeamShortResponse(Struct, kw_only=True):
    id: int
    name: str
    description: str = ""
    avatar: str | None = None

    @classmethod
    def from_model(cls, model: TeamModel) -> Self:
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            avatar=model.avatar,
        )


class TeamResponse(Struct, kw_only=True):
    id: int
    name: str
    description: str = ""
    avatar: str | None = None
    location: str = ""
    links: list[LinkResponse] = []
    captain_user_id: int | None = None
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
            avatar=model.avatar,
            location=model.location,
            links=[LinkResponse.from_dict(link) for link in (model.links or [])],
            captain_user_id=model.captain_user_id,
            users=[UserShortResponse.from_model(user) for user in model.users],
            events=[EventResponse.from_model(event) for event in events],
        )


class TeamCreateRequest(Struct, kw_only=True):
    name: str
    description: str = ""
    avatar: str | None = None
    location: str = ""
    links: list[LinkRequest] = []
    user_ids: list[int] = []

    def dump_links(self) -> list[LinkData]:
        return [link.to_domain() for link in self.links]


class TeamUpdateRequest(Struct, kw_only=True):
    name: str | None = None
    description: str | None = None
    avatar: str | None = None
    location: str | None = None
    links: list[LinkRequest] | None = None

    def dump_links(self) -> list[LinkData] | None:
        if self.links is None:
            return None
        return [link.to_domain() for link in self.links]


class TeamInviteCreateRequest(Struct, kw_only=True):
    expires_in_hours: int = 72


class TeamInviteCreateResponse(Struct, kw_only=True):
    token: str
    expires_at: datetime

    @classmethod
    def from_model(cls, model: TeamInviteModel) -> Self:
        return cls(
            token=model.token,
            expires_at=model.expires_at,
        )


class TeamJoinByInviteRequest(Struct, kw_only=True):
    token: str


class TeamTransferCaptainRequest(Struct, kw_only=True):
    new_captain_user_id: int
