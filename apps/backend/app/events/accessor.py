from datetime import UTC, datetime

from sqlalchemy import Integer, delete, func, insert, literal, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import selectinload

from app.core.accessors import BaseAccessor
from app.core.db import with_transaction
from app.events.models import EventModel, EventRatingModel


class EventAccessor(BaseAccessor):
    async def list_events(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[EventModel], int]:
        result = await self.store.db.execute(
            select(
                EventModel,
                func.count(EventModel.id).over().label("total"),
            )
            .order_by(EventModel.date.desc())
            .offset(offset)
            .limit(limit),
        )
        rows = result.all()
        if rows:
            return [row[0] for row in rows], int(rows[0][1])

        if offset == 0:
            return [], 0

        total = await self.store.db.scalar_one(select(func.count(EventModel.id)))
        return [], total

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
        return await self.store.db.scalar_one(
            insert(EventModel)
            .values(
                title=title,
                description=description,
                date=date,
                cover=cover,
                is_verify=is_verify,
            )
            .returning(EventModel),
        )

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

    async def get_event_ratings(
        self,
        event_id: int,
        *,
        status: str | None = None,
    ) -> list[EventRatingModel] | None:
        stmt = select(EventRatingModel).where(EventRatingModel.event_id == event_id)
        if status is not None:
            stmt = stmt.where(EventRatingModel.status == status)
        ratings_result = await self.store.db.scalars(
            stmt,
        )
        ratings = list(ratings_result.all())
        if ratings:
            return ratings

        event_exists = await self.store.db.scalar(
            select(EventModel.id).where(EventModel.id == event_id),
        )
        if event_exists is None:
            return None
        return []

    @with_transaction
    async def upsert_rating(
        self,
        *,
        event_id: int,
        user_id: int,
        status: str,
        team_id: int | None = None,
    ) -> EventRatingModel | None:
        awarded_at = datetime.now(UTC)
        insert_stmt = pg_insert(EventRatingModel).from_select(
            [
                EventRatingModel.event_id.key,
                EventRatingModel.user_id.key,
                EventRatingModel.status.key,
                EventRatingModel.team_id.key,
                EventRatingModel.awarded_at.key,
            ],
            select(
                EventModel.id,
                literal(user_id),
                literal(status),
                literal(team_id, type_=Integer),
                literal(awarded_at),
            ).where(EventModel.id == event_id),
        )
        return await self.store.db.scalar(
            insert_stmt
            .on_conflict_do_update(
                index_elements=[
                    EventRatingModel.event_id,
                    EventRatingModel.user_id,
                ],
                set_={
                    EventRatingModel.status.key: insert_stmt.excluded.status,
                    EventRatingModel.team_id.key: insert_stmt.excluded.team_id,
                    EventRatingModel.awarded_at.key: insert_stmt.excluded.awarded_at,
                },
            )
            .returning(EventRatingModel),
        )

    @with_transaction
    async def delete_rating(self, event_id: int, user_id: int) -> bool:
        result = await self.store.db.execute(
            delete(EventRatingModel).where(
                EventRatingModel.event_id == event_id,
                EventRatingModel.user_id == user_id,
            ),
        )
        return result.rowcount > 0
