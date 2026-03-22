from typing import NoReturn

from litestar.exceptions import NotFoundException
from msgspec import Struct

from app.core.schemas import OkResponse, PaginatedResponse


def ok[T: Struct](data: T | None = None) -> OkResponse[T]:
    return OkResponse(data=data)


def paginated[T: Struct](
    *,
    total: int,
    limit: int,
    offset: int,
    data: list[T],
) -> OkResponse[PaginatedResponse[T]]:
    return ok(
        PaginatedResponse[T](
            total=total,
            limit=limit,
            offset=offset,
            data=data,
        ),
    )


def raise_not_found(entity: str) -> NoReturn:
    raise NotFoundException(detail=f"{entity} not found")
