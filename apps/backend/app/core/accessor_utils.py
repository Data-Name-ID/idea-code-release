from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import ColumnElement, delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

if TYPE_CHECKING:
    from sqlalchemy.sql.selectable import Select

    from app.core.db import DatabaseAccessor


def collect_defined_values(**kwargs: object) -> dict[str, object]:
    return {field: value for field, value in kwargs.items() if value is not None}


def build_ilike_pattern(search: str) -> str:
    return f"%{search}%"


async def paginate_by_id[ModelT](
    *,
    db: DatabaseAccessor,
    ids_stmt: Select[tuple[int]],
    model: type[ModelT],
    model_id: Any,
    limit: int,
    offset: int,
    order_by: ColumnElement[Any] | None = None,
) -> tuple[list[ModelT], int]:
    total = int(
        await db.scalar_one(
            select(func.count()).select_from(ids_stmt.subquery()),
        ),
    )
    if total == 0:
        return [], 0

    page_ids = ids_stmt.order_by(model_id).offset(offset).limit(limit).subquery()
    stmt = select(model).join(page_ids, model_id == page_ids.c.id)
    stmt = stmt.order_by(model_id) if order_by is None else stmt.order_by(order_by)
    rows = (await db.scalars(stmt)).all()
    return list(rows), total


async def replace_m2m_relations(
    *,
    db: DatabaseAccessor,
    relation_table: Any,
    owner_column: Any,
    related_column: Any,
    owner_id: int,
    related_ids: list[int],
    related_ids_stmt: Select[tuple[int]],
) -> None:
    await db.execute(delete(relation_table).where(owner_column == owner_id))
    if not related_ids:
        return

    resolved_ids = (await db.scalars(related_ids_stmt)).all()
    values = [
        {owner_column.key: owner_id, related_column.key: item_id}
        for item_id in resolved_ids
    ]
    if not values:
        return

    await db.execute(
        pg_insert(relation_table)
        .values(values)
        .on_conflict_do_nothing(index_elements=[owner_column, related_column]),
    )
