from litestar import Controller, Request, delete, get, post, put, status_codes
from litestar.exceptions import HTTPException, PermissionDeniedException

from app.core.schemas import OkResponse, PaginatedResponse
from app.core.store import Store
from app.teams.accessor import (
    TeamInviteInvalidError,
    TeamOperationError,
    TeamPermissionDeniedError,
)
from app.teams.schemas import (
    TeamCreateRequest,
    TeamInviteCreateRequest,
    TeamInviteCreateResponse,
    TeamJoinByInviteRequest,
    TeamResponse,
    TeamShortResponse,
    TeamTransferCaptainRequest,
    TeamUpdateRequest,
)
from app.web.responses import ok, paginated, raise_not_found

INVITE_EXPIRES_MIN_HOURS = 1
INVITE_EXPIRES_MAX_HOURS = 720


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
    ) -> OkResponse[PaginatedResponse[TeamShortResponse]]:
        teams, total = await store.teams.list_teams(
            limit=limit,
            offset=offset,
            search=search,
            event_id=event_id,
            user_id=user_id,
        )
        return paginated(
            total=total,
            limit=limit,
            offset=offset,
            data=[TeamShortResponse.from_model(team) for team in teams],
        )

    @get(path="/{team_id:int}", exclude_from_auth=True)
    async def get_team(self, store: Store, team_id: int) -> OkResponse[TeamResponse]:
        team = await store.teams.get_team_by_id(team_id)
        if team is None:
            raise_not_found("Team")
        events = await store.teams.get_team_events(team.id)
        return ok(TeamResponse.from_model(team, events=events))

    @post(path="/", status_code=status_codes.HTTP_201_CREATED)
    async def create_team(
        self,
        store: Store,
        request: Request,
        data: TeamCreateRequest,
    ) -> OkResponse[TeamResponse]:
        team = await store.teams.create_team(
            name=data.name,
            description=data.description,
            avatar=data.avatar,
            location=data.location,
            links=data.dump_links(),
            captain_user_id=int(request.user.id),
            user_ids=data.user_ids,
        )
        events = await store.teams.get_team_events(team.id)
        return ok(TeamResponse.from_model(team, events=events))

    @put(path="/{team_id:int}")
    async def update_team(
        self,
        store: Store,
        request: Request,
        team_id: int,
        data: TeamUpdateRequest,
    ) -> OkResponse[TeamResponse]:
        try:
            team = await store.teams.update_team(
                team_id,
                acting_user_id=int(request.user.id),
                name=data.name,
                description=data.description,
                avatar=data.avatar,
                location=data.location,
                links=data.dump_links(),
            )
        except TeamPermissionDeniedError as exc:
            raise PermissionDeniedException(detail=str(exc)) from None

        if team is None:
            raise_not_found("Team")
        events = await store.teams.get_team_events(team.id)
        return ok(TeamResponse.from_model(team, events=events))

    @post(path="/{team_id:int}/invites", status_code=status_codes.HTTP_201_CREATED)
    async def create_invite(
        self,
        store: Store,
        request: Request,
        team_id: int,
        data: TeamInviteCreateRequest,
    ) -> OkResponse[TeamInviteCreateResponse]:
        if not (
            INVITE_EXPIRES_MIN_HOURS
            <= data.expires_in_hours
            <= INVITE_EXPIRES_MAX_HOURS
        ):
            msg = (
                f"expires_in_hours must be between "
                f"{INVITE_EXPIRES_MIN_HOURS} and {INVITE_EXPIRES_MAX_HOURS}"
            )
            raise HTTPException(status_code=400, detail=msg)

        try:
            invite = await store.teams.create_team_invite(
                team_id=team_id,
                created_by_user_id=int(request.user.id),
                expires_in_hours=data.expires_in_hours,
            )
        except TeamPermissionDeniedError as exc:
            raise PermissionDeniedException(detail=str(exc)) from None

        if invite is None:
            raise_not_found("Team")
        return ok(TeamInviteCreateResponse.from_model(invite))

    @post(path="/join-by-invite")
    async def join_by_invite(
        self,
        store: Store,
        request: Request,
        data: TeamJoinByInviteRequest,
    ) -> OkResponse[TeamResponse]:
        try:
            team = await store.teams.join_team_by_invite(
                token=data.token,
                user_id=int(request.user.id),
            )
        except TeamInviteInvalidError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from None

        events = await store.teams.get_team_events(team.id)
        return ok(TeamResponse.from_model(team, events=events))

    @delete(path="/{team_id:int}/members/{user_id:int}")
    async def remove_member(
        self,
        store: Store,
        request: Request,
        team_id: int,
        user_id: int,
    ) -> OkResponse[TeamResponse]:
        try:
            team = await store.teams.remove_team_member(
                team_id=team_id,
                acting_user_id=int(request.user.id),
                member_user_id=user_id,
            )
        except TeamPermissionDeniedError as exc:
            raise PermissionDeniedException(detail=str(exc)) from None
        except TeamOperationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from None

        if team is None:
            raise_not_found("Team")
        events = await store.teams.get_team_events(team.id)
        return ok(TeamResponse.from_model(team, events=events))

    @post(path="/{team_id:int}/captain/transfer")
    async def transfer_captain(
        self,
        store: Store,
        request: Request,
        team_id: int,
        data: TeamTransferCaptainRequest,
    ) -> OkResponse[TeamResponse]:
        try:
            team = await store.teams.transfer_team_captain(
                team_id=team_id,
                acting_user_id=int(request.user.id),
                new_captain_user_id=data.new_captain_user_id,
            )
        except TeamPermissionDeniedError as exc:
            raise PermissionDeniedException(detail=str(exc)) from None
        except TeamOperationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from None

        if team is None:
            raise_not_found("Team")
        events = await store.teams.get_team_events(team.id)
        return ok(TeamResponse.from_model(team, events=events))

    @post(path="/{team_id:int}/leave", status_code=status_codes.HTTP_204_NO_CONTENT)
    async def leave_team(
        self,
        store: Store,
        request: Request,
        team_id: int,
    ) -> None:
        try:
            left = await store.teams.leave_team(
                team_id=team_id,
                user_id=int(request.user.id),
            )
        except TeamOperationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from None

        if left is None:
            raise_not_found("Team")
