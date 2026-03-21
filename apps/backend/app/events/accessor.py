from datetime import UTC, datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import selectinload

from app.core.accessors import BaseAccessor
from app.core.db import with_single_session, with_transaction
from app.events.models import EventModel, EventRatingModel


class EventAccessor(BaseAccessor):
    @with_single_session
    async def list_events(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[EventModel], int]:
        total = await self.store.db.scalar_one(
            select(func.count(EventModel.id)),
        )
        result = await self.store.db.scalars(
            select(EventModel)
            .order_by(EventModel.date.desc())
            .offset(offset)
            .limit(limit),
        )
        return list(result.all()), total

    async def get_event_by_id(self, event_id: int) -> EventModel | None:
        return await self.store.db.scalar(
            select(EventModel)
            .options(selectinload(EventModel.ratings))
            .where(EventModel.id == event_id),
        )

    @with_transaction
    async def create_event(
        self,
        *,
        title: str,
        description: str = "",
        date: datetime,
        cover: str | None = None,
        is_verify: bool = False,
    ) -> EventModel:
        db = self.store.db
        event = EventModel(
            title=title,
            description=description,
            date=date,
            cover=cover,
            is_verify=is_verify,
        )
        db.add(event)
        await db.flush()
        await db.refresh(event)
        return event

    @with_transaction
    async def update_event(
        self,
        event_id: int,
        **kwargs: object,
    ) -> EventModel | None:
        values = {k: v for k, v in kwargs.items() if v is not None}
        if not values:
            return await self.get_event_by_id(event_id)

        return await self.store.db.scalar(
            update(EventModel)
            .where(EventModel.id == event_id)
            .values(**values)
            .returning(EventModel),
        )

    @with_transaction
    async def delete_event(self, event_id: int) -> bool:
        result = await self.store.db.execute(
            delete(EventModel).where(EventModel.id == event_id),
        )
        return result.rowcount > 0

    async def get_event_ratings(self, event_id: int) -> list[EventRatingModel]:
        result = await self.store.db.scalars(
            select(EventRatingModel).where(
                EventRatingModel.event_id == event_id,
            ),
        )
        return list(result.all())

    @with_transaction
    async def upsert_rating(
        self,
        *,
        event_id: int,
        user_id: int,
        status: str,
        team_id: int | None = None,
    ) -> EventRatingModel:
        db = self.store.db
        existing = await db.get(EventRatingModel, (event_id, user_id))
        if existing:
            existing.status = status
            existing.team_id = team_id
            existing.awarded_at = datetime.now(UTC)
            await db.flush()
            return existing

        entry = EventRatingModel(
            event_id=event_id,
            user_id=user_id,
            status=status,
            team_id=team_id,
        )
        db.add(entry)
        await db.flush()
        return entry

    @with_transaction
    async def delete_rating(self, event_id: int, user_id: int) -> bool:
        result = await self.store.db.execute(
            delete(EventRatingModel).where(
                EventRatingModel.event_id == event_id,
                EventRatingModel.user_id == user_id,
            ),
        )
        return result.rowcount > 0
