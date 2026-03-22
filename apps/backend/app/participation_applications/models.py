from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import StaticConfig
from app.core.db import BaseModel
from app.core.models.mixins import CreatedAtMixin, IDMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from app.skills.models import SkillModel
    from app.users.models import UserModel

application_skills = Table(
    "participation_application_skills",
    BaseModel.metadata,
    Column(
        "application_id",
        ForeignKey("participation_applications.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("skill_id", ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)


class ParticipationApplicationModel(IDMixin, CreatedAtMixin, UpdatedAtMixin, BaseModel):
    __tablename__ = "participation_applications"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="status_allowed",
        ),
        CheckConstraint(
            "preferred_team_format IN ('solo', 'team')",
            name="preferred_team_format_allowed",
        ),
    )

    applicant_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
    )

    comment: Mapped[str] = mapped_column(
        String(StaticConfig.LONG_STR_LENGTH),
        default="",
    )

    desired_role: Mapped[str] = mapped_column(
        String(StaticConfig.NAME_STR_LENGTH),
        default="",
    )

    preferred_team_format: Mapped[str] = mapped_column(
        String(StaticConfig.SHORT_STR_LENGTH),
        default="team",
    )

    status: Mapped[str] = mapped_column(
        String(StaticConfig.SHORT_STR_LENGTH),
        default="pending",
    )

    applicant: Mapped[UserModel] = relationship("UserModel", lazy="selectin")
    skills: Mapped[list[SkillModel]] = relationship(
        "SkillModel",
        secondary=application_skills,
        lazy="selectin",
    )
