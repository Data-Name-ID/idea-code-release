from sqlalchemy import delete, insert, select, update

from app.core.accessors import BaseAccessor
from app.core.db import with_transaction
from app.roles.models import RoleModel


class RoleAccessor(BaseAccessor):
    async def list_roles(self) -> list[RoleModel]:
        result = await self.store.db.scalars(
            select(RoleModel).order_by(RoleModel.id),
        )
        return list(result.all())

    async def get_role_by_id(self, role_id: int) -> RoleModel | None:
        return await self.store.db.scalar(
            select(RoleModel).where(RoleModel.id == role_id),
        )

    @with_transaction
    async def create_role(self, *, name: str) -> RoleModel:
        return await self.store.db.scalar_one(
            insert(RoleModel).values(name=name).returning(RoleModel),
        )

    @with_transaction
    async def update_role(self, role_id: int, *, name: str) -> RoleModel | None:
        return await self.store.db.scalar(
            update(RoleModel)
            .where(RoleModel.id == role_id)
            .values(name=name)
            .returning(RoleModel),
        )

    @with_transaction
    async def delete_role(self, role_id: int) -> bool:
        result = await self.store.db.execute(
            delete(RoleModel).where(RoleModel.id == role_id),
        )
        return result.rowcount > 0
