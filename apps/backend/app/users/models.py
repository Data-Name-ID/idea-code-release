from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import StaticConfig
from app.core.db import BaseModel
from app.core.models.mixins import CreatedAtMixin, IDMixin, UpdatedAtMixin


class UserModel(IDMixin, CreatedAtMixin, UpdatedAtMixin, BaseModel):
    __tablename__ = "users"

    email: Mapped[str | None] = mapped_column(
        String(StaticConfig.CREDENTIALS_STR_LENGTH),
        unique=True,
        nullable=True,
    )

    activated: Mapped[bool] = mapped_column(default=False)


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
