from collections.abc import Sequence

from litestar.types import ControllerRouterHandler

from app.events.views import EventController


def get_handlers() -> Sequence[ControllerRouterHandler]:
    return (EventController,)
