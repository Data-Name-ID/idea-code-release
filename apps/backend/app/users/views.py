from litestar import Controller, delete, get, post, put, status_codes
from litestar.exceptions import NotFoundException

from app.core.store import Store
from app.users.schemas import (
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserShortResponse,
    UserUpdateRequest,
)


class UserController(Controller):
    path = "/api/users"
    tags = ("users",)

    @get(path="/", exclude_from_auth=True)
    async def list_users(
        self,
        store: Store,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        role_id: int | None = None,
        skill_id: int | None = None,
    ) -> UserListResponse:
        users, total = await store.users.list_users(
            limit=limit,
            offset=offset,
            search=search,
            role_id=role_id,
            skill_id=skill_id,
        )
        return UserListResponse(
            total=total,
            limit=limit,
            offset=offset,
            data=[UserShortResponse.from_model(u) for u in users],
        )

    @post(path="/", status_code=status_codes.HTTP_201_CREATED)
    async def create_user(
        self,
        store: Store,
        data: UserCreateRequest,
    ) -> UserResponse:
        user = await store.users.create_user(
            username=data.username,
            name=data.name,
            email=data.email,
            avatar=data.avatar,
            description=data.description,
            location=data.location,
            links=data.dump_links(),
            role_ids=data.role_ids,
            skill_ids=data.skill_ids,
        )
        return UserResponse.from_model(user)

    @get(path="/{user_id:int}", exclude_from_auth=True)
    async def get_user(self, store: Store, user_id: int) -> UserResponse:
        user = await store.users.get_user_by_id(user_id)
        if user is None:
            raise NotFoundException(detail="User not found")
        return UserResponse.from_model(user)

    @put(path="/{user_id:int}")
    async def update_user(
        self,
        store: Store,
        user_id: int,
        data: UserUpdateRequest,
    ) -> UserResponse:
        user = await store.users.update_user(
            user_id,
            name=data.name,
            email=data.email,
            avatar=data.avatar,
            description=data.description,
            location=data.location,
            links=data.dump_links(),
            role_ids=data.role_ids,
            skill_ids=data.skill_ids,
        )
        if user is None:
            raise NotFoundException(detail="User not found")
        return UserResponse.from_model(user)

    @delete(path="/{user_id:int}", status_code=status_codes.HTTP_204_NO_CONTENT)
    async def delete_user(self, store: Store, user_id: int) -> None:
        deleted = await store.users.delete_user(user_id)
        if not deleted:
            raise NotFoundException(detail="User not found")
