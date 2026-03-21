from litestar import Controller, delete, get, post, put, status_codes
from litestar.exceptions import NotFoundException

from app.core.store import Store
from app.skills.schemas import SkillCreateRequest, SkillResponse, SkillUpdateRequest


class SkillController(Controller):
    path = "/api/skills"
    tags = ("skills",)

    @get(path="/", exclude_from_auth=True)
    async def list_skills(self, store: Store) -> list[SkillResponse]:
        skills = await store.skills.list_skills()
        return [SkillResponse.from_model(s) for s in skills]

    @post(path="/", status_code=status_codes.HTTP_201_CREATED)
    async def create_skill(
        self,
        store: Store,
        data: SkillCreateRequest,
    ) -> SkillResponse:
        skill = await store.skills.create_skill(name=data.name)
        return SkillResponse.from_model(skill)

    @get(path="/{skill_id:int}", exclude_from_auth=True)
    async def get_skill(self, store: Store, skill_id: int) -> SkillResponse:
        skill = await store.skills.get_skill_by_id(skill_id)
        if skill is None:
            raise NotFoundException(detail="Skill not found")
        return SkillResponse.from_model(skill)

    @put(path="/{skill_id:int}")
    async def update_skill(
        self,
        store: Store,
        skill_id: int,
        data: SkillUpdateRequest,
    ) -> SkillResponse:
        skill = await store.skills.update_skill(skill_id, name=data.name)
        if skill is None:
            raise NotFoundException(detail="Skill not found")
        return SkillResponse.from_model(skill)

    @delete(path="/{skill_id:int}", status_code=status_codes.HTTP_204_NO_CONTENT)
    async def delete_skill(self, store: Store, skill_id: int) -> None:
        deleted = await store.skills.delete_skill(skill_id)
        if not deleted:
            raise NotFoundException(detail="Skill not found")
