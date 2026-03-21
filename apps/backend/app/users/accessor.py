from datetime import datetime
from typing import cast

from sqlalchemy import Select, delete, func, insert, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import selectinload

from app.core.accessors import BaseAccessor
from app.core.db import with_transaction
from app.roles.models import RoleModel
from app.skills.models import SkillModel
from app.users.domain import AuthUser, LinkData, TelegramIdentityInput
from app.users.models import TelegramIdentityModel, UserModel, user_roles, user_skills

type AuthUserRow = tuple[
    int,
    int,
    str | None,
    str,
    str | None,
    str | None,
]


class UserAccessor(BaseAccessor):
    # ── Telegram auth ──

    @with_transaction
    async def upsert_user_from_telegram(
        self,
        *,
        telegram_identity: TelegramIdentityInput,
        auth_date: datetime,
    ) -> AuthUser:
        user_id = await self._find_user_id_by_telegram_user_id(
            telegram_user_id=telegram_identity.telegram_user_id,
        )
        if user_id is None:
            tg_id = telegram_identity.telegram_user_id
            username = telegram_identity.username or f"tg_{tg_id}"
            stmt_user_insert = (
                insert(UserModel)
                .values(
                    email=None,
                    username=username,
                    name=telegram_identity.first_name,
                    activated=True,
                )
                .returning(UserModel.id)
            )
            user_id = await self.store.db.scalar_one(stmt_user_insert)

        stmt = pg_insert(TelegramIdentityModel).values(
            user_id=user_id,
            telegram_user_id=telegram_identity.telegram_user_id,
            username=telegram_identity.username,
            first_name=telegram_identity.first_name,
            last_name=telegram_identity.last_name,
            photo_url=telegram_identity.photo_url,
            auth_date=auth_date,
        )
        stmt_update = stmt.on_conflict_do_update(
            index_elements=[TelegramIdentityModel.telegram_user_id],
            set_={
                TelegramIdentityModel.username.key: stmt.excluded.username,
                TelegramIdentityModel.first_name.key: stmt.excluded.first_name,
                TelegramIdentityModel.last_name.key: stmt.excluded.last_name,
                TelegramIdentityModel.photo_url.key: stmt.excluded.photo_url,
                TelegramIdentityModel.auth_date.key: stmt.excluded.auth_date,
            },
        )
        await self.store.db.execute(stmt_update)

        user = await self.get_auth_user(user_id=user_id)
        if user is None:
            msg = "Telegram user was not created"
            raise RuntimeError(msg)
        return user

    async def get_auth_user(self, *, user_id: int) -> AuthUser | None:
        stmt = (
            select(
                UserModel.id.label("id"),
                TelegramIdentityModel.telegram_user_id.label("telegram_user_id"),
                TelegramIdentityModel.username.label("username"),
                TelegramIdentityModel.first_name.label("first_name"),
                TelegramIdentityModel.last_name.label("last_name"),
                TelegramIdentityModel.photo_url.label("photo_url"),
            )
            .join(
                TelegramIdentityModel,
                TelegramIdentityModel.user_id == UserModel.id,
            )
            .where(UserModel.id == user_id)
        )
        row = await self.store.db.one_or_none(stmt)
        return self._build_auth_user(cast("AuthUserRow | None", row))

    async def get_auth_user_by_telegram_user_id(
        self,
        *,
        telegram_user_id: int,
    ) -> AuthUser | None:
        stmt = (
            select(
                UserModel.id.label("id"),
                TelegramIdentityModel.telegram_user_id.label("telegram_user_id"),
                TelegramIdentityModel.username.label("username"),
                TelegramIdentityModel.first_name.label("first_name"),
                TelegramIdentityModel.last_name.label("last_name"),
                TelegramIdentityModel.photo_url.label("photo_url"),
            )
            .join(
                TelegramIdentityModel,
                TelegramIdentityModel.user_id == UserModel.id,
            )
            .where(TelegramIdentityModel.telegram_user_id == telegram_user_id)
        )
        row = await self.store.db.one_or_none(stmt)
        return self._build_auth_user(cast("AuthUserRow | None", row))

    @staticmethod
    def _build_auth_user(row: AuthUserRow | None) -> AuthUser | None:
        if row is None:
            return None
        (
            resolved_user_id,
            telegram_user_id,
            username,
            first_name,
            last_name,
            photo_url,
        ) = row
        return AuthUser(
            id=resolved_user_id,
            telegram_user_id=telegram_user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            photo_url=photo_url,
        )

    async def _find_user_id_by_telegram_user_id(
        self,
        *,
        telegram_user_id: int,
    ) -> int | None:
        return await self.store.db.scalar(
            select(TelegramIdentityModel.user_id).where(
                TelegramIdentityModel.telegram_user_id == telegram_user_id,
            ),
        )

    # ── Profile CRUD ──

    async def get_user_by_id(self, user_id: int) -> UserModel | None:
        return await self.store.db.scalar(
            select(UserModel)
            .options(selectinload(UserModel.roles), selectinload(UserModel.skills))
            .where(UserModel.id == user_id),
        )

    async def list_users(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        role_id: int | None = None,
        skill_id: int | None = None,
    ) -> tuple[list[UserModel], int]:
        filtered_user_ids = self._build_filtered_user_ids_stmt(
            search=search,
            role_id=role_id,
            skill_id=skill_id,
        )
        total = int(
            await self.store.db.scalar_one(
                select(func.count()).select_from(filtered_user_ids.subquery()),
            ),
        )
        if total == 0:
            return [], 0

        page_user_ids = (
            filtered_user_ids.order_by(UserModel.id).offset(offset).limit(limit).subquery()
        )
        users = (
            await self.store.db.scalars(
                select(UserModel)
                .join(page_user_ids, UserModel.id == page_user_ids.c.id)
                .options(selectinload(UserModel.roles), selectinload(UserModel.skills))
                .order_by(UserModel.id),
            )
        ).all()
        return list(users), total

    @with_transaction
    async def create_user(
        self,
        *,
        username: str,
        name: str,
        email: str | None = None,
        avatar: str | None = None,
        description: str = "",
        location: str = "",
        links: list[LinkData] | None = None,
        role_ids: list[int] | None = None,
        skill_ids: list[int] | None = None,
    ) -> UserModel:
        user_id = await self.store.db.scalar_one(
            insert(UserModel)
            .values(
                username=username,
                name=name,
                email=email,
                avatar=avatar,
                description=description,
                location=location,
                links=self._serialize_links(links) or [],
            )
            .returning(UserModel.id),
        )
        await self._apply_relations(user_id, role_ids=role_ids, skill_ids=skill_ids)
        user = await self.get_user_by_id(user_id)
        if user is None:
            msg = "User was created but cannot be loaded"
            raise RuntimeError(msg)
        return user

    @with_transaction
    async def update_user(
        self,
        user_id: int,
        *,
        name: str | None = None,
        email: str | None = None,
        avatar: str | None = None,
        description: str | None = None,
        location: str | None = None,
        links: list[LinkData] | None = None,
        role_ids: list[int] | None = None,
        skill_ids: list[int] | None = None,
    ) -> UserModel | None:
        values = self._collect_scalar_values(
            name=name,
            email=email,
            avatar=avatar,
            description=description,
            location=location,
            links=self._serialize_links(links),
        )
        if values:
            updated_user_id = await self.store.db.scalar(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(**values)
                .returning(UserModel.id),
            )
            if updated_user_id is None:
                return None
        elif await self.get_user_by_id(user_id) is None:
            return None

        await self._apply_relations(user_id, role_ids=role_ids, skill_ids=skill_ids)
        return await self.get_user_by_id(user_id)

    @with_transaction
    async def delete_user(self, user_id: int) -> bool:
        result = await self.store.db.execute(
            delete(UserModel).where(UserModel.id == user_id),
        )
        return result.rowcount > 0

    @staticmethod
    def _collect_scalar_values(**kwargs: object) -> dict[str, object]:
        return {field: value for field, value in kwargs.items() if value is not None}

    @staticmethod
    def _build_user_search_pattern(search: str) -> str:
        return f"%{search}%"

    def _build_filtered_user_ids_stmt(
        self,
        *,
        search: str | None = None,
        role_id: int | None = None,
        skill_id: int | None = None,
    ) -> Select[tuple[int]]:
        stmt = select(UserModel.id)

        if search:
            pattern = self._build_user_search_pattern(search)
            stmt = stmt.where(
                UserModel.name.ilike(pattern) | UserModel.username.ilike(pattern),
            )

        if role_id is not None:
            stmt = stmt.join(user_roles, user_roles.c.user_id == UserModel.id).where(
                user_roles.c.role_id == role_id,
            )

        if skill_id is not None:
            stmt = stmt.join(
                user_skills,
                user_skills.c.user_id == UserModel.id,
            ).where(user_skills.c.skill_id == skill_id)

        return stmt.distinct()

    @staticmethod
    def _serialize_links(links: list[LinkData] | None) -> list[dict[str, str]] | None:
        if links is None:
            return None
        return [link.to_dict() for link in links]

    async def _apply_relations(
        self,
        user_id: int,
        *,
        role_ids: list[int] | None = None,
        skill_ids: list[int] | None = None,
    ) -> None:
        if role_ids is None and skill_ids is None:
            return

        db = self.store.db
        if role_ids is not None:
            await db.execute(delete(user_roles).where(user_roles.c.user_id == user_id))
            if role_ids:
                role_result = await db.scalars(
                    select(RoleModel.id).where(RoleModel.id.in_(role_ids)),
                )
                role_values = [
                    {"user_id": user_id, "role_id": role_id}
                    for role_id in role_result.all()
                ]
                if role_values:
                    await db.execute(
                        pg_insert(user_roles)
                        .values(role_values)
                        .on_conflict_do_nothing(
                            index_elements=[
                                user_roles.c.user_id,
                                user_roles.c.role_id,
                            ],
                        ),
                    )

        if skill_ids is not None:
            await db.execute(
                delete(user_skills).where(user_skills.c.user_id == user_id),
            )
            if skill_ids:
                skill_result = await db.scalars(
                    select(SkillModel.id).where(SkillModel.id.in_(skill_ids)),
                )
                skill_values = [
                    {"user_id": user_id, "skill_id": skill_id}
                    for skill_id in skill_result.all()
                ]
                if skill_values:
                    await db.execute(
                        pg_insert(user_skills)
                        .values(skill_values)
                        .on_conflict_do_nothing(
                            index_elements=[
                                user_skills.c.user_id,
                                user_skills.c.skill_id,
                            ],
                        ),
                    )
