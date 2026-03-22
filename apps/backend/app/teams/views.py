from litestar import Controller, delete, get, post, put, status_codes
from litestar.exceptions import NotFoundException

from app.core.store import Store
from app.teams.schemas import (
    TeamCreateRequest,
    TeamListResponse,
    TeamResponse,
    TeamShortResponse,
    TeamUpdateRequest,
)


class TeamController(Controller):
    path = "/api/teams"
    tags = ("teams",)

    @get(path="/", exclude_from_auth=True)
    async def list_teams(
        self,
        store: Store,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        event_id: int | None = None,
        user_id: int | None = None,
    ) -> TeamListResponse:
        teams, total = await store.teams.list_teams(
            limit=limit,
            offset=offset,
            search=search,
            event_id=event_id,
            user_id=user_id,
        )
        return TeamListResponse(
            total=total,
            limit=limit,
            offset=offset,
            data=[TeamShortResponse.from_model(team) for team in teams],
        )

    @post(path="/", status_code=status_codes.HTTP_201_CREATED)
    async def create_team(
        self,
        store: Store,
        data: TeamCreateRequest,
    ) -> TeamResponse:
        team = await store.teams.create_team(
            name=data.name,
            description=data.description,
            user_ids=data.user_ids,
        )
        events = await store.teams.get_team_events(team.id)
        return TeamResponse.from_model(team, events=events)

    @get(path="/{team_id:int}", exclude_from_auth=True)
    async def get_team(self, store: Store, team_id: int) -> TeamResponse:
        team = await store.teams.get_team_by_id(team_id)
        if team is None:
            raise NotFoundException(detail="Team not found")
        events = await store.teams.get_team_events(team.id)
        return TeamResponse.from_model(team, events=events)

    @put(path="/{team_id:int}")
    async def update_team(
        self,
        store: Store,
        team_id: int,
        data: TeamUpdateRequest,
    ) -> TeamResponse:
        team = await store.teams.update_team(
            team_id,
            name=data.name,
            description=data.description,
            user_ids=data.user_ids,
        )
        if team is None:
            raise NotFoundException(detail="Team not found")
        events = await store.teams.get_team_events(team.id)
        return TeamResponse.from_model(team, events=events)

    @delete(path="/{team_id:int}", status_code=status_codes.HTTP_204_NO_CONTENT)
    async def delete_team(self, store: Store, team_id: int) -> None:
        deleted = await store.teams.delete_team(team_id)
        if not deleted:
            raise NotFoundException(detail="Team not found")
