from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from sqlalchemy import func, insert, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.accessor_utils import replace_m2m_relations
from app.core.accessors import BaseAccessor
from app.core.db import with_transaction
from app.events.models import EventModel, EventRatingModel
from app.events.schemas import EventRatingStatus
from app.ingest.models import OrganizerAPITokenModel
from app.ingest.schemas import (
    OrganizerHackathonInput,
    OrganizerImportCounters,
    OrganizerImportError,
    OrganizerImportRequest,
    OrganizerImportResponse,
    OrganizerMemberInput,
    OrganizerResultInput,
    OrganizerTeamInput,
)
from app.teams.models import TeamModel, team_users
from app.users.models import TelegramIdentityModel, UserModel


class OrganizerIngestAccessor(BaseAccessor):
    async def authorize_api_key(self, *, api_key: str) -> bool:
        if not api_key:
            return False

        token_hash = self._hash_token(api_key)
        token_id = await self.store.db.scalar(
            select(OrganizerAPITokenModel.id).where(
                OrganizerAPITokenModel.token_hash == token_hash,
                OrganizerAPITokenModel.is_active.is_(True),
            ),
        )
        if token_id is None:
            return False

        await self.store.db.execute(
            update(OrganizerAPITokenModel)
            .where(OrganizerAPITokenModel.id == token_id)
            .values(last_used_at=datetime.now(UTC)),
        )
        return True

    @with_transaction
    async def import_data(
        self,
        *,
        payload: OrganizerImportRequest,
    ) -> OrganizerImportResponse:
        hackathons = OrganizerImportCounters()
        teams = OrganizerImportCounters()
        results = OrganizerImportCounters()
        errors: list[OrganizerImportError] = []

        hackathon_external_id = payload.hackathon.external_id
        hackathon_event_id = await self._upsert_hackathon(
            item=payload.hackathon,
            counters=hackathons,
            errors=errors,
        )

        for team_item in payload.teams:
            await self._upsert_team(
                item=team_item,
                counters=teams,
                errors=errors,
            )

        if hackathon_event_id is not None:
            for result_item in payload.results:
                await self._upsert_result(
                    item=result_item,
                    event_id=hackathon_event_id,
                    hackathon_external_id=hackathon_external_id,
                    counters=results,
                    errors=errors,
                )

        return OrganizerImportResponse(
            hackathons=hackathons,
            teams=teams,
            results=results,
            errors=errors,
        )

    async def _upsert_hackathon(
        self,
        *,
        item: OrganizerHackathonInput,
        counters: OrganizerImportCounters,
        errors: list[OrganizerImportError],
    ) -> int | None:
        external_id = item.external_id.strip()
        if not external_id:
            self._skip_with_error(
                errors=errors,
                counters=counters,
                entity="hackathon",
                key=item.external_id,
                detail="external_id is required",
            )
            return None

        existing_id = await self.store.db.scalar(
            select(EventModel.id).where(EventModel.external_id == external_id),
        )
        if existing_id is None:
            event_id = await self.store.db.scalar_one(
                insert(EventModel)
                .values(
                    external_id=external_id,
                    title=item.title,
                    description=item.description,
                    date=item.date,
                    cover=item.cover,
                    is_verify=True,
                )
                .returning(EventModel.id),
            )
            counters.created += 1
            return int(event_id)

        await self.store.db.execute(
            update(EventModel)
            .where(EventModel.id == existing_id)
            .values(
                title=item.title,
                description=item.description,
                date=item.date,
                cover=item.cover,
                is_verify=True,
            ),
        )
        counters.updated += 1
        return int(existing_id)

    async def _upsert_team(  # noqa: C901, PLR0912
        self,
        *,
        item: OrganizerTeamInput,
        counters: OrganizerImportCounters,
        errors: list[OrganizerImportError],
    ) -> bool:
        external_id = item.external_id.strip()
        if not external_id:
            self._skip_with_error(
                errors=errors,
                counters=counters,
                entity="team",
                key=item.name,
                detail="external_id is required",
            )
            return False

        existing = await self.store.db.one_or_none(
            select(TeamModel.id, TeamModel.external_id).where(
                TeamModel.external_id == external_id,
            ),
        )
        team_id: int | None = None
        created = False

        if existing is None:
            by_name = await self.store.db.one_or_none(
                select(TeamModel.id, TeamModel.external_id).where(
                    TeamModel.name == item.name,
                ),
            )
            if by_name is None:
                created = True
            else:
                team_id, saved_external_id = by_name
                if saved_external_id and saved_external_id != external_id:
                    self._skip_with_error(
                        errors=errors,
                        counters=counters,
                        entity="team",
                        key=external_id,
                        detail="team name is already linked to another external_id",
                    )
                    return False
        else:
            team_id = int(existing[0])

        member_ids: list[int] = []
        for member in item.members:
            user_id = await self._resolve_or_create_user(member=member)
            if user_id is None:
                self._skip_with_error(
                    errors=errors,
                    counters=counters,
                    entity="team",
                    key=external_id,
                    detail="failed to resolve team member",
                )
                return False
            member_ids.append(user_id)

        if created:
            team_id = await self.store.db.scalar_one(
                insert(TeamModel)
                .values(
                    external_id=external_id,
                    name=item.name,
                    description=item.description,
                )
                .returning(TeamModel.id),
            )
        else:
            if team_id is None:
                msg = "Team ID is not resolved"
                raise RuntimeError(msg)
            await self.store.db.execute(
                update(TeamModel)
                .where(TeamModel.id == team_id)
                .values(
                    external_id=external_id,
                    name=item.name,
                    description=item.description,
                ),
            )

        unique_member_ids = list(dict.fromkeys(member_ids))
        if team_id is None:
            msg = "Team ID is not available"
            raise RuntimeError(msg)
        await replace_m2m_relations(
            db=self.store.db,
            relation_table=team_users,
            owner_column=team_users.c.team_id,
            related_column=team_users.c.user_id,
            owner_id=team_id,
            related_ids=unique_member_ids,
            related_ids_stmt=select(UserModel.id).where(UserModel.id.in_(unique_member_ids)),
        )

        if created:
            counters.created += 1
        else:
            counters.updated += 1
        return True

    async def _upsert_result(  # noqa: PLR0911
        self,
        *,
        item: OrganizerResultInput,
        event_id: int,
        hackathon_external_id: str,
        counters: OrganizerImportCounters,
        errors: list[OrganizerImportError],
    ) -> bool:
        if item.team_external_id and item.user is not None:
            self._skip_with_error(
                errors=errors,
                counters=counters,
                entity="result",
                key=hackathon_external_id,
                detail="provide either team_external_id or user",
            )
            return False

        status, place = self._resolve_status_and_place(
            status=item.status,
            place=item.place,
        )
        if status is None or place is None:
            self._skip_with_error(
                errors=errors,
                counters=counters,
                entity="result",
                key=hackathon_external_id,
                detail="status/place are invalid",
            )
            return False

        team_id: int | None = None
        user_ids: list[int] = []

        if item.team_external_id:
            team_id = await self.store.db.scalar(
                select(TeamModel.id).where(
                    TeamModel.external_id == item.team_external_id,
                ),
            )
            if team_id is None:
                self._skip_with_error(
                    errors=errors,
                    counters=counters,
                    entity="result",
                    key=item.team_external_id,
                    detail="team not found by external_id",
                )
                return False

            raw_team_users = await self.store.db.scalars(
                select(team_users.c.user_id).where(team_users.c.team_id == team_id),
            )
            user_ids = list(raw_team_users.all())
            if not user_ids:
                self._skip_with_error(
                    errors=errors,
                    counters=counters,
                    entity="result",
                    key=item.team_external_id,
                    detail="team has no members",
                )
                return False

        elif item.user is not None:
            user_id = await self._resolve_or_create_user(member=item.user)
            if user_id is None:
                self._skip_with_error(
                    errors=errors,
                    counters=counters,
                    entity="result",
                    key=hackathon_external_id,
                    detail="failed to resolve user",
                )
                return False
            user_ids = [user_id]

        else:
            self._skip_with_error(
                errors=errors,
                counters=counters,
                entity="result",
                key=hackathon_external_id,
                detail="team_external_id or user is required",
            )
            return False

        existing_rows = await self.store.db.scalars(
            select(EventRatingModel.user_id).where(
                EventRatingModel.event_id == event_id,
                EventRatingModel.user_id.in_(user_ids),
            ),
        )
        existing_user_ids = set(existing_rows.all())

        awarded_at = item.awarded_at or datetime.now(UTC)
        for user_id in user_ids:
            insert_stmt = pg_insert(EventRatingModel).values(
                event_id=event_id,
                user_id=user_id,
                status=status,
                place=place,
                team_id=team_id,
                awarded_at=awarded_at,
            )
            await self.store.db.execute(
                insert_stmt.on_conflict_do_update(
                    index_elements=[
                        EventRatingModel.event_id,
                        EventRatingModel.user_id,
                    ],
                    set_={
                        EventRatingModel.status.key: insert_stmt.excluded.status,
                        EventRatingModel.place.key: insert_stmt.excluded.place,
                        EventRatingModel.team_id.key: insert_stmt.excluded.team_id,
                        EventRatingModel.awarded_at.key: (
                            insert_stmt.excluded.awarded_at
                        ),
                    },
                ),
            )

        if any(user_id in existing_user_ids for user_id in user_ids):
            counters.updated += 1
        else:
            counters.created += 1
        return True

    async def _resolve_or_create_user(  # noqa: C901
        self,
        *,
        member: OrganizerMemberInput,
    ) -> int | None:
        if member.telegram_id is not None:
            resolved_by_tg = await self.store.db.scalar(
                select(TelegramIdentityModel.user_id).where(
                    TelegramIdentityModel.telegram_user_id == member.telegram_id,
                ),
            )
            if resolved_by_tg is not None:
                return resolved_by_tg

        if member.email:
            resolved_by_email = await self.store.db.scalar(
                select(UserModel.id).where(UserModel.email == member.email),
            )
            if resolved_by_email is not None:
                if member.telegram_id is not None:
                    await self._upsert_telegram_identity(
                        user_id=resolved_by_email,
                        member=member,
                    )
                return resolved_by_email

        if member.username:
            resolved_by_username = await self.store.db.scalar(
                select(UserModel.id).where(UserModel.username == member.username),
            )
            if resolved_by_username is not None:
                if member.telegram_id is not None:
                    await self._upsert_telegram_identity(
                        user_id=resolved_by_username,
                        member=member,
                    )
                return resolved_by_username

        if (
            member.telegram_id is None
            and not member.email
            and not member.username
        ):
            return None

        username = member.username or await self._generate_username(member=member)
        display_name = member.name.strip() or username

        user_id = await self.store.db.scalar_one(
            insert(UserModel)
            .values(
                username=username,
                email=member.email,
                name=display_name,
                avatar=member.avatar,
                activated=True,
            )
            .returning(UserModel.id),
        )

        if member.telegram_id is not None:
            await self._upsert_telegram_identity(user_id=user_id, member=member)

        return user_id

    async def _generate_username(self, *, member: OrganizerMemberInput) -> str:
        base = "organizer_user"
        if member.telegram_id is not None:
            base = f"tg_{member.telegram_id}"
        elif member.email:
            local = member.email.split("@", maxsplit=1)[0].strip().lower()
            safe = "".join(ch for ch in local if ch.isalnum() or ch == "_")
            base = safe or base

        candidate = base
        index = 1
        while await self.store.db.scalar(
            select(func.count(UserModel.id)).where(UserModel.username == candidate),
        ):
            candidate = f"{base}_{index}"
            index += 1

        return candidate

    async def _upsert_telegram_identity(
        self,
        *,
        user_id: int,
        member: OrganizerMemberInput,
    ) -> None:
        if member.telegram_id is None:
            return

        now = datetime.now(UTC)
        first_name = (
            member.name.strip() or member.username or f"tg_{member.telegram_id}"
        )
        stmt = pg_insert(TelegramIdentityModel).values(
            user_id=user_id,
            telegram_user_id=member.telegram_id,
            username=member.username,
            first_name=first_name,
            last_name=None,
            photo_url=member.avatar,
            auth_date=now,
        )
        await self.store.db.execute(
            stmt.on_conflict_do_update(
                index_elements=[TelegramIdentityModel.telegram_user_id],
                set_={
                    TelegramIdentityModel.user_id.key: user_id,
                    TelegramIdentityModel.username.key: stmt.excluded.username,
                    TelegramIdentityModel.first_name.key: stmt.excluded.first_name,
                    TelegramIdentityModel.photo_url.key: stmt.excluded.photo_url,
                    TelegramIdentityModel.auth_date.key: stmt.excluded.auth_date,
                },
            ),
        )

    @staticmethod
    def _resolve_status_and_place(
        *,
        status: EventRatingStatus | None,
        place: int | None,
    ) -> tuple[str | None, int | None]:
        if place is not None and place <= 0:
            return None, None

        resolved_status = status.value if status is not None else None
        resolved_place = place

        if resolved_place is None and resolved_status is not None:
            resolved_place = OrganizerIngestAccessor._status_to_place(resolved_status)

        if resolved_status is None and resolved_place is not None:
            resolved_status = OrganizerIngestAccessor._place_to_status(resolved_place)

        return resolved_status, resolved_place

    @staticmethod
    def _status_to_place(status: str) -> int:
        if status == EventRatingStatus.WINNER.value:
            return 1
        if status == EventRatingStatus.PRIZE_WINNER.value:
            return 2
        return 4

    @staticmethod
    def _place_to_status(place: int) -> str:
        if place == 1:
            return EventRatingStatus.WINNER.value
        if place in {2, 3}:
            return EventRatingStatus.PRIZE_WINNER.value
        return EventRatingStatus.PARTICIPANT.value

    @staticmethod
    def _skip_with_error(
        *,
        errors: list[OrganizerImportError],
        counters: OrganizerImportCounters,
        entity: str,
        key: str,
        detail: str,
    ) -> None:
        counters.skipped += 1
        counters.errors += 1
        errors.append(
            OrganizerImportError(
                entity=entity,
                key=key,
                detail=detail,
            ),
        )

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()
