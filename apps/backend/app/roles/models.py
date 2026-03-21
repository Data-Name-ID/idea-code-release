from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import StaticConfig
from app.core.db import BaseModel
from app.core.models.mixins import IDMixin

if TYPE_CHECKING:
    from app.users.models import UserModel


class RoleModel(IDMixin, BaseModel):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(StaticConfig.NAME_STR_LENGTH),
        unique=True,
    )

    users: Mapped[list[UserModel]] = relationship(
        secondary="user_roles",
        lazy="selectin",
        back_populates="roles",
        viewonly=True,
    )
