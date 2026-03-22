from sqlalchemy import Select, delete, func, insert, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import selectinload

from app.core.accessors import BaseAccessor
from app.core.db import with_transaction
from app.events.models import EventModel, EventRatingModel
from app.teams.models import TeamModel, team_users
from app.users.models import UserModel


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
        total = int(
            await self.store.db.scalar_one(
                select(func.count()).select_from(filtered_team_ids.subquery()),
            ),
        )
        if total == 0:
            return [], 0

        page_team_ids = (
            filtered_team_ids.order_by(TeamModel.id).offset(offset).limit(limit).subquery()
        )
        teams = (
            await self.store.db.scalars(
                select(TeamModel)
                .join(page_team_ids, TeamModel.id == page_team_ids.c.id)
                .order_by(TeamModel.id),
            )
        ).all()
        return list(teams), total

    async def get_team_by_id(self, team_id: int) -> TeamModel | None:
        return await self.store.db.scalar(
            select(TeamModel)
            .options(selectinload(TeamModel.users))
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
        user_ids: list[int] | None = None,
    ) -> TeamModel:
        team_id = await self.store.db.scalar_one(
            insert(TeamModel)
            .values(name=name, description=description)
            .returning(TeamModel.id),
        )
        await self._apply_users(team_id, user_ids=user_ids)
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
        name: str | None = None,
        description: str | None = None,
        user_ids: list[int] | None = None,
    ) -> TeamModel | None:
        values = self._collect_scalar_values(
            name=name,
            description=description,
        )
        if values:
            updated_team_id = await self.store.db.scalar(
                update(TeamModel)
                .where(TeamModel.id == team_id)
                .values(**values)
                .returning(TeamModel.id),
            )
            if updated_team_id is None:
                return None
        elif await self.get_team_by_id(team_id) is None:
            return None

        await self._apply_users(team_id, user_ids=user_ids)
        return await self.get_team_by_id(team_id)

    @with_transaction
    async def delete_team(self, team_id: int) -> bool:
        result = await self.store.db.execute(
            delete(TeamModel).where(TeamModel.id == team_id),
        )
        return result.rowcount > 0

    @staticmethod
    def _collect_scalar_values(**kwargs: object) -> dict[str, object]:
        return {field: value for field, value in kwargs.items() if value is not None}

    @staticmethod
    def _build_team_search_pattern(search: str) -> str:
        return f"%{search}%"

    def _build_filtered_team_ids_stmt(
        self,
        *,
        search: str | None = None,
        event_id: int | None = None,
        user_id: int | None = None,
    ) -> Select[tuple[int]]:
        stmt = select(TeamModel.id)

        if search:
            pattern = self._build_team_search_pattern(search)
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

    async def _apply_users(
        self,
        team_id: int,
        *,
        user_ids: list[int] | None = None,
    ) -> None:
        if user_ids is None:
            return

        db = self.store.db
        await db.execute(delete(team_users).where(team_users.c.team_id == team_id))
        if not user_ids:
            return

        user_result = await db.scalars(
            select(UserModel.id).where(UserModel.id.in_(user_ids)),
        )
        user_values = [
            {"team_id": team_id, "user_id": user_id} for user_id in user_result.all()
        ]
        if not user_values:
            return

        await db.execute(
            pg_insert(team_users)
            .values(user_values)
            .on_conflict_do_nothing(
                index_elements=[
                    team_users.c.team_id,
                    team_users.c.user_id,
                ],
            ),
        )
