import hashlib
import hmac
from datetime import UTC, datetime, timedelta

from litestar.exceptions import HTTPException, PermissionDeniedException
from litestar.security.jwt import Token

from app.auth.schemas import TelegramLoginRequest
from app.core.config import TelegramConfig

ACCESS_TOKEN_TYPE = "access"  # noqa: S105
REFRESH_TOKEN_TYPE = "refresh"  # noqa: S105


class InvalidRefreshTokenError(ValueError):
    pass


def assert_telegram_auth_configured(config: TelegramConfig) -> None:
    if not config.bot_token or not config.bot_username:
        msg = "Telegram auth is not configured"
        raise HTTPException(status_code=503, detail=msg)


def get_token_type(token: Token) -> str | None:
    token_type = token.extras.get("type")
    return token_type if isinstance(token_type, str) else None


def is_refresh_token(token: Token) -> bool:
    return get_token_type(token) == REFRESH_TOKEN_TYPE


def decode_refresh_token(*, encoded_token: str, secret: str) -> Token:
    try:
        token = Token.decode(
            encoded_token=encoded_token,
            secret=secret,
            algorithm="HS256",
        )
    except (ValueError, KeyError) as exc:
        msg = "Invalid or expired refresh token"
        raise InvalidRefreshTokenError(msg) from exc
    if not is_refresh_token(token):
        msg = "Invalid token type"
        raise InvalidRefreshTokenError(msg)
    return token


def validate_telegram_login_payload(
    *,
    payload: TelegramLoginRequest,
    config: TelegramConfig,
) -> datetime:
    data_to_check: dict[str, str] = {
        "auth_date": str(payload.auth_date),
        "first_name": payload.first_name,
        "id": str(payload.id),
    }
    if payload.last_name:
        data_to_check["last_name"] = payload.last_name
    if payload.photo_url:
        data_to_check["photo_url"] = payload.photo_url
    if payload.username:
        data_to_check["username"] = payload.username

    check_string = "\n".join(
        f"{key}={data_to_check[key]}"
        for key in sorted(data_to_check)
    )
    secret_key = hashlib.sha256(config.bot_token.encode("utf-8")).digest()
    calculated_hash = hmac.new(
        key=secret_key,
        msg=check_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(calculated_hash, payload.hash):
        msg = "Invalid Telegram login payload hash"
        raise PermissionDeniedException(msg)

    auth_datetime = datetime.fromtimestamp(payload.auth_date, tz=UTC)
    now = datetime.now(tz=UTC)
    max_age = timedelta(seconds=config.auth_max_age_seconds)
    if auth_datetime > now + timedelta(minutes=1):
        msg = "Invalid Telegram auth_date"
        raise PermissionDeniedException(msg)
    if now - auth_datetime > max_age:
        msg = "Telegram login payload is expired"
        raise PermissionDeniedException(msg)

    return auth_datetime
