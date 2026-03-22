from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Self
from urllib.parse import urlparse

from msgspec import Struct

from app.roles.schemas import RoleResponse
from app.skills.schemas import SkillResponse
from app.users.domain import LinkData

if TYPE_CHECKING:
    from app.users.models import UserModel


class LinkType(StrEnum):
    TELEGRAM = "telegram"
    GITHUB = "github"
    GITLAB = "gitlab"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    OTHER = "other"


_DOMAIN_TO_LINK_TYPE: dict[str, LinkType] = {
    "t.me": LinkType.TELEGRAM,
    "telegram.me": LinkType.TELEGRAM,
    "github.com": LinkType.GITHUB,
    "gitlab.com": LinkType.GITLAB,
    "twitter.com": LinkType.TWITTER,
    "x.com": LinkType.TWITTER,
    "instagram.com": LinkType.INSTAGRAM,
    "www.instagram.com": LinkType.INSTAGRAM,
}


def detect_link_type(url: str) -> LinkType:
    try:
        host = urlparse(url).hostname or ""
    except ValueError:
        return LinkType.OTHER
    if host not in _DOMAIN_TO_LINK_TYPE:
        host = host.lower().removeprefix("www.")
    return _DOMAIN_TO_LINK_TYPE.get(host, LinkType.OTHER)


class LinkRequest(Struct, kw_only=True):
    url: str
    label: str

    def to_domain(self) -> LinkData:
        return LinkData(url=self.url, label=self.label)


class LinkResponse(Struct, kw_only=True):
    url: str
    label: str
    type: LinkType

    @classmethod
    def from_link(cls, data: LinkData) -> Self:
        return cls(
            url=data.url,
            label=data.label,
            type=detect_link_type(data.url),
        )

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Self:
        return cls.from_link(LinkData(url=data["url"], label=data["label"]))


class UserResponse(Struct, kw_only=True):
    id: int
    username: str
    email: str | None = None
    name: str
    avatar: str | None = None
    description: str = ""
    location: str = ""
    links: list[LinkResponse] = []
    roles: list[RoleResponse] = []
    skills: list[SkillResponse] = []
    open_to_teamup: bool = True

    @classmethod
    def from_model(cls, model: UserModel) -> Self:
        return cls(
            id=model.id,
            username=model.username,
            email=model.email,
            name=model.name,
            avatar=model.avatar,
            description=model.description,
            location=model.location,
            links=[LinkResponse.from_dict(link) for link in (model.links or [])],
            roles=[RoleResponse.from_model(r) for r in model.roles],
            skills=[SkillResponse.from_model(s) for s in model.skills],
            open_to_teamup=model.open_to_teamup,
        )


class UserShortResponse(Struct, kw_only=True):
    id: int
    username: str
    name: str
    avatar: str | None = None
    location: str = ""
    roles: list[RoleResponse] = []
    skills: list[SkillResponse] = []
    open_to_teamup: bool = True

    @classmethod
    def from_model(cls, model: UserModel) -> Self:
        return cls(
            id=model.id,
            username=model.username,
            name=model.name,
            avatar=model.avatar,
            location=model.location,
            roles=[RoleResponse.from_model(r) for r in model.roles],
            skills=[SkillResponse.from_model(s) for s in model.skills],
            open_to_teamup=model.open_to_teamup,
        )


class UserCreateRequest(Struct, kw_only=True):
    username: str
    email: str | None = None
    name: str
    avatar: str | None = None
    description: str = ""
    location: str = ""
    links: list[LinkRequest] = []
    role_ids: list[int] = []
    skill_ids: list[int] = []
    open_to_teamup: bool = True

    def dump_links(self) -> list[LinkData]:
        return [link.to_domain() for link in self.links]


class UserUpdateRequest(Struct, kw_only=True):
    name: str | None = None
    email: str | None = None
    avatar: str | None = None
    description: str | None = None
    location: str | None = None
    links: list[LinkRequest] | None = None
    role_ids: list[int] | None = None
    skill_ids: list[int] | None = None
    open_to_teamup: bool | None = None

    def dump_links(self) -> list[LinkData] | None:
        if self.links is None:
            return None
        return [link.to_domain() for link in self.links]
