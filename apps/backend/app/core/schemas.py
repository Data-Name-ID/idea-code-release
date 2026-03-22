from msgspec import Struct


class OkResponse[T: Struct](Struct):
    status: str = "ok"
    data: T | None = None


class PaginatedResponse[T: Struct](Struct, kw_only=True):
    total: int
    limit: int
    offset: int
    data: list[T]
