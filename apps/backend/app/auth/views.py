from typing import Any, cast

from litestar import Controller, Request, Response, get, post, status_codes
from litestar.datastructures import Cookie
from litestar.exceptions import (
    ClientException,
    NotAuthorizedException,
    NotFoundException,
)
from litestar.security.jwt import JWTCookieAuth, Token

from app.auth.password import hash_password, verify_password
from app.auth.schemas import (
    AuthResponse,
    AuthUserData,
    LoginRequest,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    TelegramConfigData,
    TelegramLoginRequest,
)
from app.auth.service import (
    assert_telegram_auth_configured,
    validate_telegram_login_payload,
)
from app.core.schemas import OkResponse
from app.core.store import Store
from app.users.domain import TelegramIdentityInput
from app.users.schemas import UserResponse


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

    # ── Email/password ──

    @post(
        path="/register",
        status_code=status_codes.HTTP_201_CREATED,
        exclude_from_auth=True,
    )
    async def register(
        self,
        store: Store,
        request: Request,
        data: RegisterRequest,
    ) -> AuthResponse:
        existing = await store.users.get_user_by_email(data.email)
        if existing is not None:
            raise ClientException(
                status_code=409,
                detail="Email already registered",
            )

        user = await store.users.create_user(
            username=data.username,
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
        )

        jwt_auth = cast("JWTCookieAuth[Any]", request.app.state["jwt_auth"])
        config = store.config.security.jwt

        access_token = jwt_auth.create_token(
            identifier=str(user.id),
            token_extras={"type": "access"},
        )
        refresh_token = jwt_auth.create_token(
            identifier=str(user.id),
            token_expiration=config.refresh_token_expiration,
            token_extras={"type": "refresh"},
        )

        return AuthResponse.from_tokens_and_model(
            access_token=access_token,
            refresh_token=refresh_token,
            jwt_config=config,
            user=user,
        )

    @post(path="/login", exclude_from_auth=True)
    async def login(
        self,
        store: Store,
        request: Request,
        data: LoginRequest,
    ) -> AuthResponse:
        user = await store.users.get_user_by_email(data.email)
        if user is None or user.password_hash is None:
            raise NotAuthorizedException(
                detail="Invalid email or password",
            )

        if not verify_password(data.password, user.password_hash):
            raise NotAuthorizedException(
                detail="Invalid email or password",
            )

        jwt_auth = cast("JWTCookieAuth[Any]", request.app.state["jwt_auth"])
        config = store.config.security.jwt

        access_token = jwt_auth.create_token(
            identifier=str(user.id),
            token_extras={"type": "access"},
        )
        refresh_token = jwt_auth.create_token(
            identifier=str(user.id),
            token_expiration=config.refresh_token_expiration,
            token_extras={"type": "refresh"},
        )

        return AuthResponse.from_tokens_and_model(
            access_token=access_token,
            refresh_token=refresh_token,
            jwt_config=config,
            user=user,
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
            token = Token.decode(
                encoded_token=data.refresh_token,
                secret=config.token_secret,
                algorithm="HS256",
            )
        except (ValueError, KeyError):
            raise NotAuthorizedException(
                detail="Invalid or expired refresh token",
            ) from None

        if token.extras.get("type") != "refresh":
            raise NotAuthorizedException(detail="Invalid token type")

        jwt_auth = cast("JWTCookieAuth[Any]", request.app.state["jwt_auth"])
        access_token = jwt_auth.create_token(
            identifier=token.sub,
            token_extras={"type": "access"},
        )

        return RefreshResponse(
            access_token=access_token,
            expires_in=int(config.token_expiration.total_seconds()),
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
