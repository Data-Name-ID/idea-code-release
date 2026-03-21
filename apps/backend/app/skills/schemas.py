from __future__ import annotations

from typing import TYPE_CHECKING, Self

from msgspec import Struct

if TYPE_CHECKING:
    from app.skills.models import SkillModel


class SkillResponse(Struct, kw_only=True):
    id: int
    name: str

    @classmethod
    def from_model(cls, model: SkillModel) -> Self:
        return cls(id=model.id, name=model.name)


class SkillCreateRequest(Struct, kw_only=True):
    name: str


class SkillUpdateRequest(Struct, kw_only=True):
    name: str
