from litestar import Controller, Request, get, post, status_codes
from litestar.exceptions import ValidationException

from app.core.schemas import OkResponse, PaginatedResponse
from app.core.store import Store
from app.events.schemas import (
    EventParticipationCreateRequest,
    EventRatingEntryResponse,
    EventRatingResponse,
    EventRatingStatus,
    EventResponse,
)
from app.web.responses import ok, paginated, raise_not_found


class EventController(Controller):
    path = "/api/events"
    tags = ("events",)

    @post(path="/participations", status_code=status_codes.HTTP_201_CREATED)
    async def create_participation(
        self,
        store: Store,
        request: Request,
        data: EventParticipationCreateRequest,
    ) -> OkResponse[EventResponse]:
        event = await store.events.create_event_participation(
            user_id=int(request.user.id),
            title=data.title,
            description=data.description,
            date=data.date,
            cover=data.cover,
            team_id=data.team_id,
        )
        if event is None:
            msg = "User is not a member of the selected team"
            raise ValidationException(detail=msg)
        return ok(EventResponse.from_model(event))

    @get(path="/", exclude_from_auth=True)
    async def list_events(
        self,
        store: Store,
        limit: int = 20,
        offset: int = 0,
    ) -> OkResponse[PaginatedResponse[EventResponse]]:
        events, total = await store.events.list_events(limit=limit, offset=offset)
        return paginated(
            total=total,
            limit=limit,
            offset=offset,
            data=[EventResponse.from_model(e) for e in events],
        )

    @get(path="/{event_id:int}", exclude_from_auth=True)
    async def get_event(self, store: Store, event_id: int) -> OkResponse[EventResponse]:
        event = await store.events.get_event_by_id(event_id)
        if event is None:
            raise_not_found("Event")
        return ok(EventResponse.from_model(event))

    @get(path="/{event_id:int}/ratings", exclude_from_auth=True)
    async def get_ratings(
        self,
        store: Store,
        event_id: int,
        status: EventRatingStatus | None = None,
    ) -> OkResponse[EventRatingResponse]:
        ratings = await store.events.get_event_ratings(
            event_id,
            status=status.value if status is not None else None,
        )
        if ratings is None:
            raise_not_found("Event")

        return ok(
            EventRatingResponse(
                event_id=event_id,
                ratings=[EventRatingEntryResponse.from_model(r) for r in ratings],
            ),
        )
