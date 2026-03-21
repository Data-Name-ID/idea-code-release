from collections.abc import Sequence

from litestar.types import ControllerRouterHandler

from app.roles.views import RoleController


def get_handlers() -> Sequence[ControllerRouterHandler]:
    return (RoleController,)
