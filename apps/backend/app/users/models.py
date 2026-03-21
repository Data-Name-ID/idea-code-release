from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import StaticConfig
from app.core.db import BaseModel
from app.core.models.mixins import CreatedAtMixin, IDMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from app.roles.models import RoleModel
    from app.skills.models import SkillModel

user_roles = Table(
    "user_roles",
    BaseModel.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

user_skills = Table(
    "user_skills",
    BaseModel.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)


class UserModel(IDMixin, CreatedAtMixin, UpdatedAtMixin, BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(StaticConfig.NAME_STR_LENGTH),
        unique=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(StaticConfig.CREDENTIALS_STR_LENGTH),
        unique=True,
        nullable=True,
        default=None,
    )

    name: Mapped[str] = mapped_column(
        String(StaticConfig.NAME_STR_LENGTH),
        default="",
    )

    avatar: Mapped[str | None] = mapped_column(
        String(StaticConfig.URL_STR_LENGTH),
        nullable=True,
        default=None,
    )

    description: Mapped[str] = mapped_column(
        String(StaticConfig.LONG_STR_LENGTH),
        default="",
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

    activated: Mapped[bool] = mapped_column(default=False)

    roles: Mapped[list[RoleModel]] = relationship(
        secondary=user_roles,
        lazy="selectin",
        back_populates="users",
    )

    skills: Mapped[list[SkillModel]] = relationship(
        secondary=user_skills,
        lazy="selectin",
        back_populates="users",
    )


class TelegramIdentityModel(IDMixin, CreatedAtMixin, UpdatedAtMixin, BaseModel):
    __tablename__ = "telegram_identities"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
    )
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str | None] = mapped_column(
        String(StaticConfig.NAME_STR_LENGTH),
        nullable=True,
    )
    first_name: Mapped[str] = mapped_column(String(StaticConfig.NAME_STR_LENGTH))
    last_name: Mapped[str | None] = mapped_column(
        String(StaticConfig.NAME_STR_LENGTH),
        nullable=True,
    )
    photo_url: Mapped[str | None] = mapped_column(
        String(StaticConfig.URL_STR_LENGTH),
        nullable=True,
    )
    auth_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
