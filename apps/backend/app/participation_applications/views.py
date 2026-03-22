from litestar import Controller, Request, get, patch, post, status_codes
from litestar.exceptions import ValidationException

from app.core.schemas import OkResponse, PaginatedResponse
from app.core.store import Store
from app.participation_applications.schemas import (
    ParticipationApplicationCreateRequest,
    ParticipationApplicationResponse,
    ParticipationApplicationStatus,
    ParticipationApplicationStatusUpdateRequest,
)
from app.web.responses import ok, paginated, raise_not_found


class ParticipationApplicationController(Controller):
    path = "/api/participation-applications"
    tags = ("participation_applications",)

    @post(path="/", status_code=status_codes.HTTP_201_CREATED)
    async def create_application(
        self,
        store: Store,
        request: Request,
        data: ParticipationApplicationCreateRequest,
    ) -> OkResponse[ParticipationApplicationResponse]:
        created = await store.participation_applications.create_application(
            applicant_user_id=int(request.user.id),
            event_id=data.event_id,
            comment=data.comment,
            desired_role=data.desired_role,
            preferred_team_format=data.preferred_team_format.value,
            skill_ids=data.skill_ids,
        )
        if created is None:
            msg = "Event does not exist"
            raise ValidationException(detail=msg)
        return ok(ParticipationApplicationResponse.from_model(created))

    @get(path="/")
    async def list_applications(
        self,
        store: Store,
        limit: int = 20,
        offset: int = 0,
        event_id: int | None = None,
        status: ParticipationApplicationStatus | None = None,
        applicant_user_id: int | None = None,
    ) -> OkResponse[PaginatedResponse[ParticipationApplicationResponse]]:
        items, total = await store.participation_applications.list_applications(
            limit=limit,
            offset=offset,
            event_id=event_id,
            status=status.value if status is not None else None,
            applicant_user_id=applicant_user_id,
        )
        return paginated(
            total=total,
            limit=limit,
            offset=offset,
            data=[ParticipationApplicationResponse.from_model(item) for item in items],
        )

    @patch(path="/{application_id:int}/status")
    async def update_status(
        self,
        store: Store,
        application_id: int,
        data: ParticipationApplicationStatusUpdateRequest,
    ) -> OkResponse[ParticipationApplicationResponse]:
        updated = await store.participation_applications.update_status(
            application_id=application_id,
            status=data.status.value,
        )
        if updated is None:
            raise_not_found("Participation application")
        return ok(ParticipationApplicationResponse.from_model(updated))
