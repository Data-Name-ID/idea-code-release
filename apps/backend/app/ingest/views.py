from litestar import Controller, Request, post
from litestar.exceptions import NotAuthorizedException

from app.core.schemas import OkResponse
from app.core.store import Store
from app.ingest.schemas import OrganizerImportRequest, OrganizerImportResponse
from app.web.responses import ok


class OrganizerIngestController(Controller):
    path = "/api/public/organizer"
    tags = ("organizer-ingest",)

    @post(path="/import", exclude_from_auth=True)
    async def import_data(
        self,
        store: Store,
        request: Request,
        data: OrganizerImportRequest,
    ) -> OkResponse[OrganizerImportResponse]:
        api_key = request.headers.get("x-api-key", "") or request.headers.get(
            "X-API-Key",
            "",
        )
        authorized = await store.organizer_ingest.authorize_api_key(api_key=api_key)
        if not authorized:
            msg = "Invalid organizer API key"
            raise NotAuthorizedException(detail=msg)

        result = await store.organizer_ingest.import_data(payload=data)
        return ok(result)
