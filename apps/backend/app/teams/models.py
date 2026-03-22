from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import StaticConfig
from app.core.db import BaseModel
from app.core.models.mixins import CreatedAtMixin, IDMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from app.users.models import UserModel

team_users = Table(
    "team_users",
    BaseModel.metadata,
    Column("team_id", ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class TeamModel(IDMixin, CreatedAtMixin, UpdatedAtMixin, BaseModel):
    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(
        String(StaticConfig.NAME_STR_LENGTH),
        unique=True,
    )
    description: Mapped[str] = mapped_column(
        String(StaticConfig.LONG_STR_LENGTH),
        default="",
    )

    users: Mapped[list[UserModel]] = relationship(
        secondary=team_users,
        lazy="selectin",
    )
