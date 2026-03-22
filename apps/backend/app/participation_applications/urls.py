from collections.abc import Sequence

from litestar.types import ControllerRouterHandler

from app.participation_applications.views import ParticipationApplicationController


def get_handlers() -> Sequence[ControllerRouterHandler]:
    return (ParticipationApplicationController,)
