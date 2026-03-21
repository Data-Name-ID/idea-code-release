from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from app.core.accessors import BaseAccessor
from app.core.db import with_single_session, with_transaction
from app.roles.models import RoleModel
from app.skills.models import SkillModel
from app.users.domain import AuthUser, TelegramIdentityInput
from app.users.models import TelegramIdentityModel, UserModel, user_roles, user_skills


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

        stmt = insert(TelegramIdentityModel).values(
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

    @with_single_session
    async def get_user_by_id(self, user_id: int) -> UserModel | None:
        return await self.store.db.scalar(
            select(UserModel)
            .options(selectinload(UserModel.roles), selectinload(UserModel.skills))
            .where(UserModel.id == user_id),
        )

    @with_single_session
    async def list_users(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        role_id: int | None = None,
        skill_id: int | None = None,
    ) -> tuple[list[UserModel], int]:
        stmt = select(UserModel).options(
            selectinload(UserModel.roles),
            selectinload(UserModel.skills),
        )
        count_stmt = select(func.count(UserModel.id))

        if search:
            pattern = f"%{search}%"
            filter_clause = UserModel.name.ilike(pattern) | UserModel.username.ilike(
                pattern,
            )
            stmt = stmt.where(filter_clause)
            count_stmt = count_stmt.where(filter_clause)

        if role_id is not None:
            stmt = stmt.join(user_roles).where(user_roles.c.role_id == role_id)
            count_stmt = count_stmt.join(user_roles).where(
                user_roles.c.role_id == role_id,
            )

        if skill_id is not None:
            stmt = stmt.join(user_skills).where(user_skills.c.skill_id == skill_id)
            count_stmt = count_stmt.join(user_skills).where(
                user_skills.c.skill_id == skill_id,
            )

        total = await self.store.db.scalar_one(count_stmt)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.store.db.scalars(stmt)
        return list(result.all()), total

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
        links: list[dict] | None = None,
        role_ids: list[int] | None = None,
        skill_ids: list[int] | None = None,
    ) -> UserModel:
        db = self.store.db
        user = UserModel(
            username=username,
            name=name,
            email=email,
            avatar=avatar,
            description=description,
            location=location,
            links=links or [],
        )
        db.add(user)
        await db.flush()
        await self._apply_relations(user, role_ids=role_ids, skill_ids=skill_ids)
        await db.flush()
        await db.refresh(user, attribute_names=["roles", "skills"])
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
        links: list[dict] | None = None,
        role_ids: list[int] | None = None,
        skill_ids: list[int] | None = None,
    ) -> UserModel | None:
        db = self.store.db
        user = await db.get(UserModel, user_id)
        if user is None:
            return None

        self._apply_scalar_fields(
            user,
            name=name,
            email=email,
            avatar=avatar,
            description=description,
            location=location,
            links=links,
        )
        await self._apply_relations(user, role_ids=role_ids, skill_ids=skill_ids)
        await db.flush()
        await db.refresh(user, attribute_names=["roles", "skills"])
        return user

    @with_transaction
    async def delete_user(self, user_id: int) -> bool:
        result = await self.store.db.execute(
            delete(UserModel).where(UserModel.id == user_id),
        )
        return result.rowcount > 0

    @staticmethod
    def _apply_scalar_fields(user: UserModel, **kwargs: object) -> None:
        for field, value in kwargs.items():
            if value is not None:
                setattr(user, field, value)

    async def _apply_relations(
        self,
        user: UserModel,
        *,
        role_ids: list[int] | None = None,
        skill_ids: list[int] | None = None,
    ) -> None:
        if role_ids is None and skill_ids is None:
            return

        db = self.store.db
        attrs = []
        if role_ids is not None:
            attrs.append("roles")
        if skill_ids is not None:
            attrs.append("skills")
        await db.refresh(user, attribute_names=attrs)

        if role_ids is not None:
            result = await db.scalars(
                select(RoleModel).where(RoleModel.id.in_(role_ids)),
            )
            user.roles = list(result.all())

        if skill_ids is not None:
            result = await db.scalars(
                select(SkillModel).where(SkillModel.id.in_(skill_ids)),
            )
            user.skills = list(result.all())
