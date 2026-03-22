from collections.abc import Sequence

from litestar.types import ControllerRouterHandler

from app.ingest.views import OrganizerIngestController


def get_handlers() -> Sequence[ControllerRouterHandler]:
    return (OrganizerIngestController,)
