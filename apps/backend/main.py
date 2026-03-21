from typing import Any

from litestar import Litestar, get
from litestar.config.cors import CORSConfig
from litestar.connection import ASGIConnection
from litestar.datastructures import State
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.openapi.spec.license import License
from litestar.security.jwt import JWTCookieAuth, Token

import app.auth.urls as auth_urls
import app.events.urls as events_urls
import app.roles.urls as roles_urls
import app.skills.urls as skills_urls
import app.users.urls as users_urls
from app.core.config import create_config
from app.core.store import Store
from app.users.domain import UserAuth
from app.web.plugins import InitPlugin

config = create_config()
store = Store(config=config)


def retrieve_user_handler(
    token: Token,
    _: ASGIConnection[Any, Any, Any, Any],
) -> UserAuth | None:
    if token.extras.get("type") == "refresh":
        return None
    return UserAuth(id=int(token.sub))


jwt_auth = JWTCookieAuth[UserAuth](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=config.security.jwt.token_secret,
    default_token_expiration=config.security.jwt.token_expiration,
    exclude=[
        "/docs",
        "/openapi.json",
        "/health",
        "/api/auth/telegram/config",
        "/api/auth/telegram/login",
        "/api/auth/refresh",
    ],
    key=config.security.cookie.key,
    path=config.security.cookie.path,
    domain=config.security.cookie.domain,
    secure=config.security.cookie.secure,
    samesite=config.security.cookie.samesite,
)


@get("/health", sync_to_thread=False)
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app = Litestar(
    route_handlers=(
        healthcheck,
        *auth_urls.get_handlers(),
        *users_urls.get_handlers(),
        *roles_urls.get_handlers(),
        *skills_urls.get_handlers(),
        *events_urls.get_handlers(),
    ),
    on_app_init=[
        jwt_auth.on_app_init,
    ],
    state=State(
        {
            "jwt_auth": jwt_auth,
        },
    ),
    plugins=(
        InitPlugin(
            store=store,
        ),
    ),
    cors_config=CORSConfig(
        allow_origins=config.security.cors_allowed_origins,
        allow_credentials=config.security.cors_allow_credentials,
    ),
    openapi_config=OpenAPIConfig(
        title="api",
        path="/docs",
        version="1.0.0",
        root_schema_site="swagger",
        license=License(
            name="MIT",
            url="https://opensource.org/licenses/MIT",
            identifier="MIT",
        ),
        render_plugins=[ScalarRenderPlugin()],
    ),
)
