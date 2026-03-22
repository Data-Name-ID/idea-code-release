from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import JSONB
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

    external_id: Mapped[str | None] = mapped_column(
        String(StaticConfig.NAME_STR_LENGTH),
        unique=True,
        nullable=True,
        default=None,
    )

    name: Mapped[str] = mapped_column(
        String(StaticConfig.NAME_STR_LENGTH),
        unique=True,
    )
    description: Mapped[str] = mapped_column(
        String(StaticConfig.LONG_STR_LENGTH),
        default="",
    )
    avatar: Mapped[str | None] = mapped_column(
        String(StaticConfig.URL_STR_LENGTH),
        nullable=True,
        default=None,
    )
    location: Mapped[str] = mapped_column(
        String(StaticConfig.NAME_STR_LENGTH),
        default="",
    )
    links: Mapped[list[dict]] = mapped_column(
        JSONB,
        default=list,
        server_default="[]",
    )
    captain_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    users: Mapped[list[UserModel]] = relationship(
        secondary=team_users,
        lazy="selectin",
    )
    captain: Mapped[UserModel | None] = relationship(
        foreign_keys=[captain_user_id],
        lazy="selectin",
    )


class TeamInviteModel(IDMixin, CreatedAtMixin, UpdatedAtMixin, BaseModel):
    __tablename__ = "team_invites"

    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"),
    )
    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )
    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
