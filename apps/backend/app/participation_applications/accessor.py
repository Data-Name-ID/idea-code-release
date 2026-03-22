from sqlalchemy import Select, func, insert, literal, select, update
from sqlalchemy.orm import selectinload

from app.core.accessor_utils import replace_m2m_relations
from app.core.accessors import BaseAccessor
from app.core.db import with_transaction
from app.events.models import EventModel
from app.participation_applications.models import (
    ParticipationApplicationModel,
    application_skills,
)
from app.skills.models import SkillModel


class ParticipationApplicationAccessor(BaseAccessor):
    async def list_applications(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        event_id: int | None = None,
        status: str | None = None,
        applicant_user_id: int | None = None,
    ) -> tuple[list[ParticipationApplicationModel], int]:
        filtered_ids = self._build_filtered_ids_stmt(
            event_id=event_id,
            status=status,
            applicant_user_id=applicant_user_id,
        )
        total = int(
            await self.store.db.scalar_one(
                select(func.count()).select_from(filtered_ids.subquery()),
            ),
        )
        if total == 0:
            return [], 0

        page_ids = (
            filtered_ids.order_by(
                ParticipationApplicationModel.created_at.desc(),
                ParticipationApplicationModel.id.desc(),
            )
            .offset(offset)
            .limit(limit)
            .subquery()
        )

        rows = (
            await self.store.db.scalars(
                select(ParticipationApplicationModel)
                .options(
                    selectinload(ParticipationApplicationModel.skills),
                    selectinload(ParticipationApplicationModel.applicant),
                )
                .join(page_ids, ParticipationApplicationModel.id == page_ids.c.id)
                .order_by(
                    ParticipationApplicationModel.created_at.desc(),
                    ParticipationApplicationModel.id.desc(),
                ),
            )
        ).all()
        return list(rows), total

    async def get_application_by_id(
        self,
        application_id: int,
    ) -> ParticipationApplicationModel | None:
        return await self.store.db.scalar(
            select(ParticipationApplicationModel)
            .options(
                selectinload(ParticipationApplicationModel.skills),
                selectinload(ParticipationApplicationModel.applicant),
            )
            .where(ParticipationApplicationModel.id == application_id),
        )

    @with_transaction
    async def create_application(
        self,
        *,
        applicant_user_id: int,
        event_id: int,
        comment: str = "",
        desired_role: str = "",
        preferred_team_format: str = "team",
        skill_ids: list[int] | None = None,
    ) -> ParticipationApplicationModel | None:
        application_id = await self.store.db.scalar(
            insert(ParticipationApplicationModel)
            .from_select(
                [
                    ParticipationApplicationModel.applicant_user_id.key,
                    ParticipationApplicationModel.event_id.key,
                    ParticipationApplicationModel.comment.key,
                    ParticipationApplicationModel.desired_role.key,
                    ParticipationApplicationModel.preferred_team_format.key,
                    ParticipationApplicationModel.status.key,
                ],
                select(
                    literal(applicant_user_id),
                    EventModel.id,
                    literal(comment),
                    literal(desired_role),
                    literal(preferred_team_format),
                    literal("pending"),
                ).where(EventModel.id == event_id),
            )
            .returning(ParticipationApplicationModel.id),
        )
        if application_id is None:
            return None

        await self._apply_skills(application_id=application_id, skill_ids=skill_ids)
        return await self.get_application_by_id(application_id)

    @with_transaction
    async def update_status(
        self,
        *,
        application_id: int,
        status: str,
    ) -> ParticipationApplicationModel | None:
        updated_id = await self.store.db.scalar(
            update(ParticipationApplicationModel)
            .where(ParticipationApplicationModel.id == application_id)
            .values(status=status)
            .returning(ParticipationApplicationModel.id),
        )
        if updated_id is None:
            return None
        return await self.get_application_by_id(updated_id)

    def _build_filtered_ids_stmt(
        self,
        *,
        event_id: int | None = None,
        status: str | None = None,
        applicant_user_id: int | None = None,
    ) -> Select[tuple[int]]:
        stmt = select(ParticipationApplicationModel.id)

        if event_id is not None:
            stmt = stmt.where(ParticipationApplicationModel.event_id == event_id)
        if status is not None:
            stmt = stmt.where(ParticipationApplicationModel.status == status)
        if applicant_user_id is not None:
            stmt = stmt.where(
                ParticipationApplicationModel.applicant_user_id == applicant_user_id,
            )

        return stmt

    async def _apply_skills(
        self,
        *,
        application_id: int,
        skill_ids: list[int] | None,
    ) -> None:
        if skill_ids is None:
            return

        await replace_m2m_relations(
            db=self.store.db,
            relation_table=application_skills,
            owner_column=application_skills.c.application_id,
            related_column=application_skills.c.skill_id,
            owner_id=application_id,
            related_ids=skill_ids,
            related_ids_stmt=select(SkillModel.id).where(SkillModel.id.in_(skill_ids)),
        )
