from collections.abc import Sequence

from litestar.types import ControllerRouterHandler

from app.teams.views import TeamController


def get_handlers() -> Sequence[ControllerRouterHandler]:
    return (TeamController,)
