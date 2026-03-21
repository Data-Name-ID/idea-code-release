from typing import TYPE_CHECKING, cast

from litestar import Controller, Request, Response, get, post, status_codes
from litestar.datastructures import Cookie
from litestar.exceptions import NotAuthorizedException

if TYPE_CHECKING:
    from litestar.security.jwt import JWTCookieAuth

from app.auth.schemas import AuthUserData, TelegramConfigData, TelegramLoginRequest
from app.auth.service import (
    assert_telegram_auth_configured,
    validate_telegram_login_payload,
)
from app.core.schemas import OkResponse
from app.core.store import Store
from app.users.domain import TelegramIdentityInput, UserAuth


class AuthController(Controller):
    path = "/api/auth"
    tags = ("auth",)

    @get(
        path="telegram/config",
        status_code=status_codes.HTTP_200_OK,
        exclude_from_auth=True,
    )
    async def telegram_config(self, store: Store) -> OkResponse[TelegramConfigData]:
        telegram_config = store.config.security.telegram
        assert_telegram_auth_configured(telegram_config)
        return OkResponse(
            data=TelegramConfigData(bot_username=telegram_config.bot_username),
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
        telegram_config = store.config.security.telegram
        assert_telegram_auth_configured(telegram_config)

        auth_date = validate_telegram_login_payload(
            payload=data,
            config=telegram_config,
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
        jwt_auth = cast("JWTCookieAuth", request.app.state["jwt_auth"])
        return jwt_auth.login(
            identifier=str(user.id),
            response_status_code=status_codes.HTTP_200_OK,
            response_body=OkResponse(data=AuthUserData.from_domain(user)),
        )

    @get(path="me", status_code=status_codes.HTTP_200_OK)
    async def me(self, store: Store, request: Request) -> OkResponse[AuthUserData]:
        auth = cast("UserAuth | None", request.user)
        if auth is None:
            msg = "Unauthorized"
            raise NotAuthorizedException(msg)
        user = await store.users.get_auth_user(user_id=auth.id)
        if user is None:
            msg = "Unauthorized"
            raise NotAuthorizedException(msg)
        return OkResponse(data=AuthUserData.from_domain(user))

    @post(path="logout", status_code=status_codes.HTTP_200_OK)
    async def logout(self, request: Request) -> Response[OkResponse]:
        jwt_auth = cast("JWTCookieAuth", request.app.state["jwt_auth"])
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
