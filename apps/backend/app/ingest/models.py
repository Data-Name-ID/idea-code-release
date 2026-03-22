from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import StaticConfig
from app.core.db import BaseModel
from app.core.models.mixins import CreatedAtMixin, IDMixin, UpdatedAtMixin


class OrganizerAPITokenModel(IDMixin, CreatedAtMixin, UpdatedAtMixin, BaseModel):
    __tablename__ = "organizer_api_tokens"

    name: Mapped[str] = mapped_column(String(StaticConfig.NAME_STR_LENGTH))
    token_hash: Mapped[str] = mapped_column(
        String(StaticConfig.CREDENTIALS_STR_LENGTH),
        unique=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
