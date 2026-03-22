from litestar import Controller, delete, get, post, put, status_codes

from app.core.schemas import OkResponse, PaginatedResponse
from app.core.store import Store
from app.roles.schemas import RoleCreateRequest, RoleResponse, RoleUpdateRequest
from app.web.responses import ok, paginated, raise_not_found


class RoleController(Controller):
    path = "/api/roles"
    tags = ("roles",)

    @get(path="/", exclude_from_auth=True)
    async def list_roles(
        self,
        store: Store,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
    ) -> OkResponse[PaginatedResponse[RoleResponse]]:
        roles, total = await store.roles.list_roles(
            limit=limit,
            offset=offset,
            search=search,
        )
        return paginated(
            total=total,
            limit=limit,
            offset=offset,
            data=[RoleResponse.from_model(r) for r in roles],
        )

    @post(path="/", status_code=status_codes.HTTP_201_CREATED)
    async def create_role(
        self,
        store: Store,
        data: RoleCreateRequest,
    ) -> OkResponse[RoleResponse]:
        role = await store.roles.create_role(name=data.name)
        return ok(RoleResponse.from_model(role))

    @get(path="/{role_id:int}", exclude_from_auth=True)
    async def get_role(self, store: Store, role_id: int) -> OkResponse[RoleResponse]:
        role = await store.roles.get_role_by_id(role_id)
        if role is None:
            raise_not_found("Role")
        return ok(RoleResponse.from_model(role))

    @put(path="/{role_id:int}")
    async def update_role(
        self,
        store: Store,
        role_id: int,
        data: RoleUpdateRequest,
    ) -> OkResponse[RoleResponse]:
        role = await store.roles.update_role(role_id, name=data.name)
        if role is None:
            raise_not_found("Role")
        return ok(RoleResponse.from_model(role))

    @delete(path="/{role_id:int}", status_code=status_codes.HTTP_204_NO_CONTENT)
    async def delete_role(self, store: Store, role_id: int) -> None:
        deleted = await store.roles.delete_role(role_id)
        if not deleted:
            raise_not_found("Role")
