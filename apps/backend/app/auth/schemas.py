from __future__ import annotations

from typing import TYPE_CHECKING, Self

from msgspec import Struct

if TYPE_CHECKING:
    from app.users.domain import AuthUser


# ── Telegram ──

class TelegramLoginRequest(Struct, kw_only=True):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


class TelegramConfigData(Struct, kw_only=True):
    bot_username: str


class DevAuthByTelegramIdRequest(Struct, kw_only=True):
    telegram_user_id: int


class AuthUserData(Struct, kw_only=True):
    id: int
    telegram_user_id: int
    username: str | None
    first_name: str
    last_name: str | None
    photo_url: str | None

    @classmethod
    def from_domain(cls, user: AuthUser) -> Self:
        return cls(
            id=user.id,
            telegram_user_id=user.telegram_user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            photo_url=user.photo_url,
        )


class RefreshRequest(Struct, kw_only=True):
    refresh_token: str


class RefreshResponse(Struct, kw_only=True):
    access_token: str
    token_type: str = "Bearer"  # noqa: S105
    expires_in: int


class DevAuthByTelegramIdResponse(Struct, kw_only=True):
    access_token: str
    token_type: str = "Bearer"  # noqa: S105
    expires_in: int
