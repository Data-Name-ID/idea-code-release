from __future__ import annotations

from typing import TYPE_CHECKING, Self

from msgspec import Struct

from app.core import validators
from app.users.schemas import UserResponse

if TYPE_CHECKING:
    from app.core.config import JWTConfig
    from app.users.domain import AuthUser
    from app.users.models import UserModel


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


# ── Email/password ──

class RegisterRequest(Struct, kw_only=True):
    username: str
    email: str
    password: str
    name: str

    def __post_init__(self) -> None:
        self.email = validators.validate_and_normalize_email(self.email)
        validators.validate_password(self.password)


class LoginRequest(Struct, kw_only=True):
    email: str
    password: str

    def __post_init__(self) -> None:
        self.email = validators.validate_and_normalize_email(self.email)


class RefreshRequest(Struct, kw_only=True):
    refresh_token: str


class AuthResponse(Struct, kw_only=True):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"  # noqa: S105
    expires_in: int
    user: UserResponse

    @classmethod
    def from_tokens_and_model(
        cls,
        *,
        access_token: str,
        refresh_token: str,
        jwt_config: JWTConfig,
        user: UserModel,
    ) -> Self:
        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(jwt_config.token_expiration.total_seconds()),
            user=UserResponse.from_model(user),
        )


class RefreshResponse(Struct, kw_only=True):
    access_token: str
    token_type: str = "Bearer"  # noqa: S105
    expires_in: int
