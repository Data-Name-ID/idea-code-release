from typing import TYPE_CHECKING, Any, cast

from litestar import Controller, Request, Response, get, post, status_codes
from litestar.datastructures import Cookie
from litestar.exceptions import (
    NotAuthorizedException,
    NotFoundException,
)

from app.auth.schemas import (
    AuthUserData,
    DevAuthByTelegramIdRequest,
    DevAuthByTelegramIdResponse,
    RefreshRequest,
    RefreshResponse,
    TelegramConfigData,
    TelegramLoginRequest,
)
from app.auth.service import (
    ACCESS_TOKEN_TYPE,
    InvalidRefreshTokenError,
    assert_telegram_auth_configured,
    decode_refresh_token,
    validate_telegram_login_payload,
)
from app.core.schemas import OkResponse
from app.core.store import Store
from app.users.domain import TelegramIdentityInput
from app.users.schemas import UserResponse

if TYPE_CHECKING:
    from litestar.security.jwt import JWTCookieAuth


class AuthController(Controller):
    path = "/api/auth"
    tags = ("auth",)

    # ── Telegram ──

    @get(
        path="telegram/config",
        status_code=status_codes.HTTP_200_OK,
        exclude_from_auth=True,
    )
    async def telegram_config(
        self,
        store: Store,
    ) -> OkResponse[TelegramConfigData]:
        telegram_cfg = store.config.security.telegram
        assert_telegram_auth_configured(telegram_cfg)
        return OkResponse(
            data=TelegramConfigData(bot_username=telegram_cfg.bot_username),
        )

    @post(
        path="telegram/login",
        status_code=status_codes.HTTP_200_OK,
        exclude_from_auth=True,
    )
    async def telegram_login(
        self,
        store: Store,
        request: Request,
        data: TelegramLoginRequest,
    ) -> Response[OkResponse[AuthUserData]]:
        telegram_cfg = store.config.security.telegram
        assert_telegram_auth_configured(telegram_cfg)

        auth_date = validate_telegram_login_payload(
            payload=data,
            config=telegram_cfg,
        )
        user = await store.users.upsert_user_from_telegram(
            telegram_identity=TelegramIdentityInput(
                telegram_user_id=data.id,
                username=data.username,
                first_name=data.first_name,
                last_name=data.last_name,
                photo_url=data.photo_url,
            ),
            auth_date=auth_date,
        )
        jwt_auth = cast("JWTCookieAuth[Any]", request.app.state["jwt_auth"])
        return jwt_auth.login(
            identifier=str(user.id),
            response_status_code=status_codes.HTTP_200_OK,
            response_body=OkResponse(data=AuthUserData.from_domain(user)),
        )

    @post(path="/refresh", exclude_from_auth=True)
    async def refresh(
        self,
        store: Store,
        request: Request,
        data: RefreshRequest,
    ) -> RefreshResponse:
        config = store.config.security.jwt

        try:
            token = decode_refresh_token(
                encoded_token=data.refresh_token,
                secret=config.token_secret,
            )
        except InvalidRefreshTokenError as exc:
            raise NotAuthorizedException(
                detail=str(exc),
            ) from None

        jwt_auth = cast("JWTCookieAuth[Any]", request.app.state["jwt_auth"])
        access_token = jwt_auth.create_token(
            identifier=token.sub,
            token_extras={"type": ACCESS_TOKEN_TYPE},
        )

        return RefreshResponse(
            access_token=access_token,
            expires_in=int(config.token_expiration.total_seconds()),
        )

    @post(
        path="dev/telegram/token",
        status_code=status_codes.HTTP_200_OK,
        exclude_from_auth=True,
    )
    async def dev_telegram_token(
        self,
        store: Store,
        request: Request,
        data: DevAuthByTelegramIdRequest,
    ) -> OkResponse[DevAuthByTelegramIdResponse]:
        if not store.config.security.dev_auth_by_tg_id_enabled:
            raise NotFoundException(detail="Not found")

        user = await store.users.get_auth_user_by_telegram_user_id(
            telegram_user_id=data.telegram_user_id,
        )
        if user is None:
            raise NotFoundException(detail="Telegram identity not found")

        jwt_auth = cast("JWTCookieAuth[Any]", request.app.state["jwt_auth"])
        access_token = jwt_auth.create_token(
            identifier=str(user.id),
            token_extras={"type": ACCESS_TOKEN_TYPE},
        )
        return OkResponse(
            data=DevAuthByTelegramIdResponse(
                access_token=access_token,
                expires_in=int(store.config.security.jwt.token_expiration.total_seconds()),
            ),
        )

    # ── Common ──

    @get(path="/me")
    async def me(
        self,
        store: Store,
        request: Request,
    ) -> UserResponse:
        user_id = int(request.user.id)
        user = await store.users.get_user_by_id(user_id)
        if user is None:
            raise NotFoundException(detail="User not found")
        return UserResponse.from_model(user)

    @post(path="logout", status_code=status_codes.HTTP_200_OK)
    async def logout(
        self,
        request: Request,
    ) -> Response[OkResponse]:
        jwt_auth = cast("JWTCookieAuth[Any]", request.app.state["jwt_auth"])
        cookie = Cookie(
            key=jwt_auth.key,
            value="",
            path=jwt_auth.path,
            max_age=0,
            domain=jwt_auth.domain,
            secure=jwt_auth.secure,
            httponly=True,
            samesite=jwt_auth.samesite,
        )
        return Response(
            content=OkResponse(),
            status_code=status_codes.HTTP_200_OK,
            cookies=[cookie],
        )
