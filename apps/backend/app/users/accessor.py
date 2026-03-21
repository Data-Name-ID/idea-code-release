from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.core.accessors import BaseAccessor
from app.core.db import with_transaction
from app.users.domain import AuthUser, TelegramIdentityInput
from app.users.models import TelegramIdentityModel, UserModel


class UserAccessor(BaseAccessor):
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
            stmt_user_insert = (
                insert(UserModel)
                .values(email=None, activated=True)
                .returning(UserModel.id)
            )
            user_id = await self.store.db.scalar_one(stmt_user_insert)

        stmt = (
            insert(TelegramIdentityModel)
            .values(
                user_id=user_id,
                telegram_user_id=telegram_identity.telegram_user_id,
                username=telegram_identity.username,
                first_name=telegram_identity.first_name,
                last_name=telegram_identity.last_name,
                photo_url=telegram_identity.photo_url,
                auth_date=auth_date,
            )
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
            .join(TelegramIdentityModel, TelegramIdentityModel.user_id == UserModel.id)
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
        stmt = select(TelegramIdentityModel.user_id).where(
            TelegramIdentityModel.telegram_user_id == telegram_user_id,
        )
        return await self.store.db.scalar(stmt)
