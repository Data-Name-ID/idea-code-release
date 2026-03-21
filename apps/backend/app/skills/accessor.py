from sqlalchemy import delete, insert, select, update

from app.core.accessors import BaseAccessor
from app.core.db import with_transaction
from app.skills.models import SkillModel


class SkillAccessor(BaseAccessor):
    async def list_skills(self) -> list[SkillModel]:
        result = await self.store.db.scalars(
            select(SkillModel).order_by(SkillModel.id),
        )
        return list(result.all())

    async def get_skill_by_id(self, skill_id: int) -> SkillModel | None:
        return await self.store.db.scalar(
            select(SkillModel).where(SkillModel.id == skill_id),
        )

    @with_transaction
    async def create_skill(self, *, name: str) -> SkillModel:
        return await self.store.db.scalar_one(
            insert(SkillModel).values(name=name).returning(SkillModel),
        )

    @with_transaction
    async def update_skill(self, skill_id: int, *, name: str) -> SkillModel | None:
        return await self.store.db.scalar(
            update(SkillModel)
            .where(SkillModel.id == skill_id)
            .values(name=name)
            .returning(SkillModel),
        )

    @with_transaction
    async def delete_skill(self, skill_id: int) -> bool:
        result = await self.store.db.execute(
            delete(SkillModel).where(SkillModel.id == skill_id),
        )
        return result.rowcount > 0
