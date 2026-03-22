from app.core.named_crud_accessor import NamedCRUDAccessor
from app.skills.models import SkillModel


class SkillAccessor(NamedCRUDAccessor[SkillModel]):
    model = SkillModel
    model_id = SkillModel.id
    model_name = SkillModel.name

    async def list_skills(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
    ) -> tuple[list[SkillModel], int]:
        return await self.list_entities(limit=limit, offset=offset, search=search)

    async def get_skill_by_id(self, skill_id: int) -> SkillModel | None:
        return await self.get_entity_by_id(skill_id)

    async def create_skill(self, *, name: str) -> SkillModel:
        return await self.create_entity(name=name)

    async def update_skill(self, skill_id: int, *, name: str) -> SkillModel | None:
        return await self.update_entity(skill_id, name=name)

    async def delete_skill(self, skill_id: int) -> bool:
        return await self.delete_entity(skill_id)
