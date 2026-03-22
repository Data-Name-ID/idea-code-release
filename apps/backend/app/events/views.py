from litestar import Controller, delete, get, post, put, status_codes

from app.core.schemas import OkResponse, PaginatedResponse
from app.core.store import Store
from app.events.schemas import (
    EventCreateRequest,
    EventRatingCreateRequest,
    EventRatingEntryResponse,
    EventRatingResponse,
    EventRatingStatus,
    EventResponse,
    EventUpdateRequest,
)
from app.web.responses import ok, paginated, raise_not_found


class EventController(Controller):
    path = "/api/events"
    tags = ("events",)

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

    @post(path="/", status_code=status_codes.HTTP_201_CREATED)
    async def create_event(
        self,
        store: Store,
        data: EventCreateRequest,
    ) -> OkResponse[EventResponse]:
        event = await store.events.create_event(
            title=data.title,
            description=data.description,
            date=data.date,
            cover=data.cover,
            is_verify=data.is_verify,
        )
        return ok(EventResponse.from_model(event))

    @get(path="/{event_id:int}", exclude_from_auth=True)
    async def get_event(self, store: Store, event_id: int) -> OkResponse[EventResponse]:
        event = await store.events.get_event_by_id(event_id)
        if event is None:
            raise_not_found("Event")
        return ok(EventResponse.from_model(event))

    @put(path="/{event_id:int}")
    async def update_event(
        self,
        store: Store,
        event_id: int,
        data: EventUpdateRequest,
    ) -> OkResponse[EventResponse]:
        event = await store.events.update_event(
            event_id,
            title=data.title,
            description=data.description,
            date=data.date,
            cover=data.cover,
            is_verify=data.is_verify,
        )
        if event is None:
            raise_not_found("Event")
        return ok(EventResponse.from_model(event))

    @delete(path="/{event_id:int}", status_code=status_codes.HTTP_204_NO_CONTENT)
    async def delete_event(self, store: Store, event_id: int) -> None:
        deleted = await store.events.delete_event(event_id)
        if not deleted:
            raise_not_found("Event")

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

    @post(
        path="/{event_id:int}/ratings",
        status_code=status_codes.HTTP_201_CREATED,
    )
    async def add_rating(
        self,
        store: Store,
        event_id: int,
        data: EventRatingCreateRequest,
    ) -> OkResponse[EventRatingEntryResponse]:
        entry = await store.events.upsert_rating(
            event_id=event_id,
            user_id=data.user_id,
            status=data.status,
            team_id=data.team_id,
        )
        if entry is None:
            raise_not_found("Event")
        return ok(EventRatingEntryResponse.from_model(entry))

    @delete(
        path="/{event_id:int}/ratings/{user_id:int}",
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    async def delete_rating(
        self,
        store: Store,
        event_id: int,
        user_id: int,
    ) -> None:
        deleted = await store.events.delete_rating(event_id, user_id)
        if not deleted:
            raise_not_found("Rating entry")
