from __future__ import annotations

from typing import TYPE_CHECKING, Self

from msgspec import Struct

if TYPE_CHECKING:
    from app.roles.models import RoleModel


class RoleResponse(Struct, kw_only=True):
    id: int
    name: str

    @classmethod
    def from_model(cls, model: RoleModel) -> Self:
        return cls(id=model.id, name=model.name)


class RoleCreateRequest(Struct, kw_only=True):
    name: str


class RoleUpdateRequest(Struct, kw_only=True):
    name: str
