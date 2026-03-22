from __future__ import annotations

from datetime import datetime  # noqa: TC003
from enum import StrEnum
from typing import TYPE_CHECKING, Self

from msgspec import Struct

from app.skills.schemas import SkillResponse
from app.users.schemas import UserShortResponse

if TYPE_CHECKING:
    from app.participation_applications.models import ParticipationApplicationModel


class ParticipationApplicationStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PreferredTeamFormat(StrEnum):
    SOLO = "solo"
    TEAM = "team"


class ParticipationApplicationResponse(Struct, kw_only=True):
    id: int
    applicant_user_id: int
    event_id: int
    comment: str = ""
    desired_role: str = ""
    preferred_team_format: PreferredTeamFormat
    status: ParticipationApplicationStatus
    skills: list[SkillResponse] = []
    applicant: UserShortResponse | None = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, model: ParticipationApplicationModel) -> Self:
        return cls(
            id=model.id,
            applicant_user_id=model.applicant_user_id,
            event_id=model.event_id,
            comment=model.comment,
            desired_role=model.desired_role,
            preferred_team_format=PreferredTeamFormat(model.preferred_team_format),
            status=ParticipationApplicationStatus(model.status),
            skills=[SkillResponse.from_model(item) for item in model.skills],
            applicant=(
                UserShortResponse.from_model(model.applicant)
                if model.applicant
                else None
            ),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class ParticipationApplicationCreateRequest(Struct, kw_only=True):
    event_id: int
    comment: str = ""
    desired_role: str = ""
    preferred_team_format: PreferredTeamFormat = PreferredTeamFormat.TEAM
    skill_ids: list[int] = []


class ParticipationApplicationStatusUpdateRequest(Struct, kw_only=True):
    status: ParticipationApplicationStatus
