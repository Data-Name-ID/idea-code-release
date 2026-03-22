from datetime import datetime
from typing import cast

from sqlalchemy import Select, delete, func, insert, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import selectinload

from app.core.accessor_utils import (
    build_ilike_pattern,
    collect_defined_values,
    replace_m2m_relations,
)
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
        location: str | None = None,
        role_id: int | None = None,
        skill_id: int | None = None,
        open_to_teamup: bool | None = None,
    ) -> tuple[list[UserModel], int]:
        filtered_user_ids = self._build_filtered_user_ids_stmt(
            search=search,
            location=location,
            role_id=role_id,
            skill_id=skill_id,
            open_to_teamup=open_to_teamup,
        )
        total = int(
            await self.store.db.scalar_one(
                select(func.count()).select_from(filtered_user_ids.subquery()),
            ),
        )
        if total == 0:
            return [], 0

        page_ids = (
            filtered_user_ids.order_by(UserModel.updated_at.desc(), UserModel.id.desc())
            .offset(offset)
            .limit(limit)
            .subquery()
        )
        users = list(
            (
                await self.store.db.scalars(
                    select(UserModel)
                    .options(
                        selectinload(UserModel.roles),
                        selectinload(UserModel.skills),
                    )
                    .join(page_ids, UserModel.id == page_ids.c.id)
                    .order_by(UserModel.updated_at.desc(), UserModel.id.desc()),
                )
            ).all(),
        )
        return users, total

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
        open_to_teamup: bool = True,
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
                open_to_teamup=open_to_teamup,
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
        open_to_teamup: bool | None = None,
    ) -> UserModel | None:
        values = collect_defined_values(
            name=name,
            email=email,
            avatar=avatar,
            description=description,
            location=location,
            links=self._serialize_links(links),
            open_to_teamup=open_to_teamup,
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

    def _build_filtered_user_ids_stmt(
        self,
        *,
        search: str | None = None,
        location: str | None = None,
        role_id: int | None = None,
        skill_id: int | None = None,
        open_to_teamup: bool | None = None,
    ) -> Select[tuple[int]]:
        stmt = select(UserModel.id)

        if search:
            pattern = build_ilike_pattern(search)
            stmt = stmt.where(
                UserModel.name.ilike(pattern)
                | UserModel.username.ilike(pattern)
                | UserModel.description.ilike(pattern)
                | UserModel.location.ilike(pattern),
            )
        if location:
            stmt = stmt.where(UserModel.location.ilike(build_ilike_pattern(location)))

        if role_id is not None:
            stmt = stmt.where(
                select(user_roles.c.user_id)
                .where(
                    user_roles.c.user_id == UserModel.id,
                    user_roles.c.role_id == role_id,
                )
                .exists(),
            )

        if skill_id is not None:
            stmt = stmt.where(
                select(user_skills.c.user_id)
                .where(
                    user_skills.c.user_id == UserModel.id,
                    user_skills.c.skill_id == skill_id,
                )
                .exists(),
            )
        if open_to_teamup is not None:
            stmt = stmt.where(UserModel.open_to_teamup.is_(open_to_teamup))

        return stmt

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
            await replace_m2m_relations(
                db=db,
                relation_table=user_roles,
                owner_column=user_roles.c.user_id,
                related_column=user_roles.c.role_id,
                owner_id=user_id,
                related_ids=role_ids,
                related_ids_stmt=select(RoleModel.id).where(RoleModel.id.in_(role_ids)),
            )

        if skill_ids is not None:
            await replace_m2m_relations(
                db=db,
                relation_table=user_skills,
                owner_column=user_skills.c.user_id,
                related_column=user_skills.c.skill_id,
                owner_id=user_id,
                related_ids=skill_ids,
                related_ids_stmt=select(SkillModel.id).where(SkillModel.id.in_(skill_ids)),
            )
