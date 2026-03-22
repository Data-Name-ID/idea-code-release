from __future__ import annotations

from typing import Any

from sqlalchemy import delete, func, insert, select, update

from app.core.accessors import BaseAccessor
from app.core.db import with_transaction


class NamedCRUDAccessor[ModelT](BaseAccessor):
    model: type[ModelT]
    model_id: Any
    model_name: Any

    async def list_entities(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
    ) -> tuple[list[ModelT], int]:
        stmt = select(self.model)
        total_stmt = select(func.count()).select_from(self.model)
        if search:
            pattern = f"%{search}%"
            search_filter = self.model_name.ilike(pattern)
            stmt = stmt.where(search_filter)
            total_stmt = total_stmt.where(search_filter)

        total = int(await self.store.db.scalar_one(total_stmt))
        if total == 0:
            return [], 0

        rows = (
            await self.store.db.scalars(
                stmt.order_by(self.model_id).offset(offset).limit(limit),
            )
        ).all()
        return list(rows), total

    async def get_entity_by_id(self, entity_id: int) -> ModelT | None:
        return await self.store.db.scalar(
            select(self.model).where(self.model_id == entity_id),
        )

    @with_transaction
    async def create_entity(self, *, name: str) -> ModelT:
        return await self.store.db.scalar_one(
            insert(self.model).values(name=name).returning(self.model),
        )

    @with_transaction
    async def update_entity(self, entity_id: int, *, name: str) -> ModelT | None:
        return await self.store.db.scalar(
            update(self.model)
            .where(self.model_id == entity_id)
            .values(name=name)
            .returning(self.model),
        )

    @with_transaction
    async def delete_entity(self, entity_id: int) -> bool:
        result = await self.store.db.execute(
            delete(self.model).where(self.model_id == entity_id),
        )
        return result.rowcount > 0
