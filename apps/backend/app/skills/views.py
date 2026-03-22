from litestar import Controller, delete, get, post, put, status_codes

from app.core.schemas import OkResponse, PaginatedResponse
from app.core.store import Store
from app.skills.schemas import SkillCreateRequest, SkillResponse, SkillUpdateRequest
from app.web.responses import ok, paginated, raise_not_found


class SkillController(Controller):
    path = "/api/skills"
    tags = ("skills",)

    @get(path="/", exclude_from_auth=True)
    async def list_skills(
        self,
        store: Store,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
    ) -> OkResponse[PaginatedResponse[SkillResponse]]:
        skills, total = await store.skills.list_skills(
            limit=limit,
            offset=offset,
            search=search,
        )
        return paginated(
            total=total,
            limit=limit,
            offset=offset,
            data=[SkillResponse.from_model(s) for s in skills],
        )

    @post(path="/", status_code=status_codes.HTTP_201_CREATED)
    async def create_skill(
        self,
        store: Store,
        data: SkillCreateRequest,
    ) -> OkResponse[SkillResponse]:
        skill = await store.skills.create_skill(name=data.name)
        return ok(SkillResponse.from_model(skill))

    @get(path="/{skill_id:int}", exclude_from_auth=True)
    async def get_skill(self, store: Store, skill_id: int) -> OkResponse[SkillResponse]:
        skill = await store.skills.get_skill_by_id(skill_id)
        if skill is None:
            raise_not_found("Skill")
        return ok(SkillResponse.from_model(skill))

    @put(path="/{skill_id:int}")
    async def update_skill(
        self,
        store: Store,
        skill_id: int,
        data: SkillUpdateRequest,
    ) -> OkResponse[SkillResponse]:
        skill = await store.skills.update_skill(skill_id, name=data.name)
        if skill is None:
            raise_not_found("Skill")
        return ok(SkillResponse.from_model(skill))

    @delete(path="/{skill_id:int}", status_code=status_codes.HTTP_204_NO_CONTENT)
    async def delete_skill(self, store: Store, skill_id: int) -> None:
        deleted = await store.skills.delete_skill(skill_id)
        if not deleted:
            raise_not_found("Skill")
