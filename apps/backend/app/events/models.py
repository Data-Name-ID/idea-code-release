from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import func

from app.core.config import StaticConfig
from app.core.db import BaseModel
from app.core.models.mixins import CreatedAtMixin, IDMixin, UpdatedAtMixin


class EventModel(IDMixin, CreatedAtMixin, UpdatedAtMixin, BaseModel):
    __tablename__ = "events"

    title: Mapped[str] = mapped_column(String(StaticConfig.NAME_STR_LENGTH))

    description: Mapped[str] = mapped_column(
        String(StaticConfig.LONG_STR_LENGTH),
        default="",
    )

    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    cover: Mapped[str | None] = mapped_column(
        String(StaticConfig.URL_STR_LENGTH),
        nullable=True,
        default=None,
    )

    is_verify: Mapped[bool] = mapped_column(default=False)

    ratings: Mapped[list["EventRatingModel"]] = relationship(
        back_populates="event",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class EventRatingModel(BaseModel):
    __tablename__ = "event_ratings"

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    status: Mapped[str] = mapped_column(
        String(StaticConfig.SHORT_STR_LENGTH),
    )

    team_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=None,
    )

    awarded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
    )

    event: Mapped["EventModel"] = relationship(back_populates="ratings")
