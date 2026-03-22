from app.core.named_crud_accessor import NamedCRUDAccessor
from app.roles.models import RoleModel


class RoleAccessor(NamedCRUDAccessor[RoleModel]):
    model = RoleModel
    model_id = RoleModel.id
    model_name = RoleModel.name

    async def list_roles(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
    ) -> tuple[list[RoleModel], int]:
        return await self.list_entities(limit=limit, offset=offset, search=search)

    async def get_role_by_id(self, role_id: int) -> RoleModel | None:
        return await self.get_entity_by_id(role_id)

    async def create_role(self, *, name: str) -> RoleModel:
        return await self.create_entity(name=name)

    async def update_role(self, role_id: int, *, name: str) -> RoleModel | None:
        return await self.update_entity(role_id, name=name)

    async def delete_role(self, role_id: int) -> bool:
        return await self.delete_entity(role_id)
