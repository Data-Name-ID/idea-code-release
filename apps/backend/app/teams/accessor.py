from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import Select, delete, insert, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import selectinload

from app.core.accessor_utils import (
    build_ilike_pattern,
    collect_defined_values,
    paginate_by_id,
    replace_m2m_relations,
)
from app.core.accessors import BaseAccessor
from app.core.db import with_transaction
from app.events.models import EventModel, EventRatingModel
from app.teams.models import TeamInviteModel, TeamModel, team_users
from app.users.models import UserModel

if TYPE_CHECKING:
    from app.users.domain import LinkData


class TeamPermissionDeniedError(PermissionError):
    pass


class TeamOperationError(ValueError):
    pass


class TeamInviteInvalidError(TeamOperationError):
    pass


class TeamAccessor(BaseAccessor):
    async def list_teams(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        event_id: int | None = None,
        user_id: int | None = None,
    ) -> tuple[list[TeamModel], int]:
        filtered_team_ids = self._build_filtered_team_ids_stmt(
            search=search,
            event_id=event_id,
            user_id=user_id,
        )
        return await paginate_by_id(
            db=self.store.db,
            ids_stmt=filtered_team_ids,
            model=TeamModel,
            model_id=TeamModel.id,
            limit=limit,
            offset=offset,
        )

    async def get_team_by_id(self, team_id: int) -> TeamModel | None:
        return await self.store.db.scalar(
            select(TeamModel)
            .options(selectinload(TeamModel.users), selectinload(TeamModel.captain))
            .where(TeamModel.id == team_id),
        )

    async def get_team_events(self, team_id: int) -> list[EventModel]:
        result = await self.store.db.scalars(
            select(EventModel)
            .join(EventRatingModel, EventRatingModel.event_id == EventModel.id)
            .where(EventRatingModel.team_id == team_id)
            .order_by(EventModel.date.desc())
            .distinct(EventModel.id),
        )
        return list(result.all())

    @with_transaction
    async def create_team(
        self,
        *,
        name: str,
        description: str = "",
        avatar: str | None = None,
        location: str = "",
        links: list[LinkData] | None = None,
        captain_user_id: int,
        user_ids: list[int] | None = None,
    ) -> TeamModel:
        member_ids = self._merge_member_ids(captain_user_id, user_ids)
        team_id = await self.store.db.scalar_one(
            insert(TeamModel)
            .values(
                name=name,
                description=description,
                avatar=avatar,
                location=location,
                links=self._serialize_links(links) or [],
                captain_user_id=captain_user_id,
            )
            .returning(TeamModel.id),
        )
        await self._apply_users(team_id, user_ids=member_ids)
        team = await self.get_team_by_id(team_id)
        if team is None:
            msg = "Team was created but cannot be loaded"
            raise RuntimeError(msg)
        return team

    @with_transaction
    async def update_team(
        self,
        team_id: int,
        *,
        acting_user_id: int,
        name: str | None = None,
        description: str | None = None,
        avatar: str | None = None,
        location: str | None = None,
        links: list[LinkData] | None = None,
    ) -> TeamModel | None:
        team = await self.get_team_by_id(team_id)
        if team is None:
            return None
        self._assert_team_captain(team=team, acting_user_id=acting_user_id)

        values = collect_defined_values(
            name=name,
            description=description,
            avatar=avatar,
            location=location,
            links=self._serialize_links(links),
        )
        if values:
            await self.store.db.execute(
                update(TeamModel).where(TeamModel.id == team_id).values(**values),
            )
        return await self.get_team_by_id(team_id)

    @with_transaction
    async def create_team_invite(
        self,
        *,
        team_id: int,
        created_by_user_id: int,
        expires_in_hours: int = 72,
    ) -> TeamInviteModel | None:
        team = await self.get_team_by_id(team_id)
        if team is None:
            return None
        self._assert_team_captain(team=team, acting_user_id=created_by_user_id)

        return await self.store.db.scalar_one(
            insert(TeamInviteModel)
            .values(
                team_id=team_id,
                token=secrets.token_urlsafe(24),
                created_by_user_id=created_by_user_id,
                expires_at=datetime.now(UTC) + timedelta(hours=expires_in_hours),
            )
            .returning(TeamInviteModel),
        )

    @with_transaction
    async def join_team_by_invite(
        self,
        *,
        token: str,
        user_id: int,
    ) -> TeamModel:
        now = datetime.now(UTC)
        invite = await self.store.db.scalar(
            select(TeamInviteModel).where(TeamInviteModel.token == token),
        )
        if invite is None:
            msg = "Invite link is invalid"
            raise TeamInviteInvalidError(msg)
        if invite.revoked_at is not None:
            msg = "Invite link was revoked"
            raise TeamInviteInvalidError(msg)
        if invite.used_at is not None:
            msg = "Invite link is already used"
            raise TeamInviteInvalidError(msg)
        if invite.expires_at <= now:
            msg = "Invite link is expired"
            raise TeamInviteInvalidError(msg)

        team_id = await self.store.db.scalar(
            update(TeamInviteModel)
            .where(
                TeamInviteModel.id == invite.id,
                TeamInviteModel.used_at.is_(None),
                TeamInviteModel.revoked_at.is_(None),
                TeamInviteModel.expires_at > now,
            )
            .values(
                used_by_user_id=user_id,
                used_at=now,
            )
            .returning(TeamInviteModel.team_id),
        )
        if team_id is None:
            msg = "Invite link is no longer valid"
            raise TeamInviteInvalidError(msg)

        await self.store.db.execute(
            pg_insert(team_users)
            .values(team_id=team_id, user_id=user_id)
            .on_conflict_do_nothing(
                index_elements=[team_users.c.team_id, team_users.c.user_id],
            ),
        )

        team = await self.get_team_by_id(team_id)
        if team is None:
            msg = "Team for invite was not found"
            raise RuntimeError(msg)
        return team

    @with_transaction
    async def remove_team_member(
        self,
        *,
        team_id: int,
        acting_user_id: int,
        member_user_id: int,
    ) -> TeamModel | None:
        team = await self.get_team_by_id(team_id)
        if team is None:
            return None
        self._assert_team_captain(team=team, acting_user_id=acting_user_id)
        if team.captain_user_id == member_user_id:
            msg = "Captain cannot be removed from the team"
            raise TeamOperationError(msg)

        result = await self.store.db.execute(
            delete(team_users).where(
                team_users.c.team_id == team_id,
                team_users.c.user_id == member_user_id,
            ),
        )
        if result.rowcount == 0:
            msg = "User is not a member of this team"
            raise TeamOperationError(msg)
        return await self.get_team_by_id(team_id)

    @with_transaction
    async def transfer_team_captain(
        self,
        *,
        team_id: int,
        acting_user_id: int,
        new_captain_user_id: int,
    ) -> TeamModel | None:
        team = await self.get_team_by_id(team_id)
        if team is None:
            return None
        self._assert_team_captain(team=team, acting_user_id=acting_user_id)

        if new_captain_user_id == team.captain_user_id:
            return team

        new_captain_member_id = await self.store.db.scalar(
            select(team_users.c.user_id).where(
                team_users.c.team_id == team_id,
                team_users.c.user_id == new_captain_user_id,
            ),
        )
        if new_captain_member_id is None:
            msg = "New captain must be a member of this team"
            raise TeamOperationError(msg)

        await self.store.db.execute(
            update(TeamModel)
            .where(TeamModel.id == team_id)
            .values(captain_user_id=new_captain_user_id),
        )
        return await self.get_team_by_id(team_id)

    @with_transaction
    async def leave_team(self, *, team_id: int, user_id: int) -> bool | None:
        team = await self.get_team_by_id(team_id)
        if team is None:
            return None
        if team.captain_user_id == user_id:
            msg = "Captain must transfer captain role before leaving"
            raise TeamOperationError(msg)

        result = await self.store.db.execute(
            delete(team_users).where(
                team_users.c.team_id == team_id,
                team_users.c.user_id == user_id,
            ),
        )
        if result.rowcount == 0:
            msg = "User is not a member of this team"
            raise TeamOperationError(msg)
        return True

    @with_transaction
    async def delete_team(self, team_id: int) -> bool:
        result = await self.store.db.execute(
            delete(TeamModel).where(TeamModel.id == team_id),
        )
        return result.rowcount > 0

    def _build_filtered_team_ids_stmt(
        self,
        *,
        search: str | None = None,
        event_id: int | None = None,
        user_id: int | None = None,
    ) -> Select[tuple[int]]:
        stmt = select(TeamModel.id)

        if search:
            pattern = build_ilike_pattern(search)
            stmt = stmt.where(
                TeamModel.name.ilike(pattern) | TeamModel.description.ilike(pattern),
            )

        if event_id is not None:
            stmt = stmt.join(
                EventRatingModel,
                EventRatingModel.team_id == TeamModel.id,
            ).where(EventRatingModel.event_id == event_id)

        if user_id is not None:
            stmt = stmt.join(team_users, team_users.c.team_id == TeamModel.id).where(
                team_users.c.user_id == user_id,
            )

        return stmt.distinct()

    @staticmethod
    def _serialize_links(links: list[LinkData] | None) -> list[dict[str, str]] | None:
        if links is None:
            return None
        return [link.to_dict() for link in links]

    @staticmethod
    def _merge_member_ids(
        captain_user_id: int,
        user_ids: list[int] | None,
    ) -> list[int]:
        ordered_ids = [captain_user_id, *(user_ids or [])]
        return list(dict.fromkeys(ordered_ids))

    @staticmethod
    def _assert_team_captain(*, team: TeamModel, acting_user_id: int) -> None:
        if team.captain_user_id != acting_user_id:
            msg = "Only team captain can perform this action"
            raise TeamPermissionDeniedError(msg)

    async def _apply_users(
        self,
        team_id: int,
        *,
        user_ids: list[int] | None = None,
    ) -> None:
        if user_ids is None:
            return

        await replace_m2m_relations(
            db=self.store.db,
            relation_table=team_users,
            owner_column=team_users.c.team_id,
            related_column=team_users.c.user_id,
            owner_id=team_id,
            related_ids=user_ids,
            related_ids_stmt=select(UserModel.id).where(UserModel.id.in_(user_ids)),
        )
