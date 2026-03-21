from collections.abc import Sequence

from litestar.types import ControllerRouterHandler

from app.skills.views import SkillController


def get_handlers() -> Sequence[ControllerRouterHandler]:
    return (SkillController,)
