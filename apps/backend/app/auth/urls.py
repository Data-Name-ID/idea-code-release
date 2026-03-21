from collections.abc import Sequence

from litestar.types import ControllerRouterHandler

from app.auth.views import AuthController


def get_handlers() -> Sequence[ControllerRouterHandler]:
    return (AuthController,)
