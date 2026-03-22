from app.core.config import Config
from app.core.object_storage import ObjectStorageService


class Store:
    def __init__(self, *, config: Config) -> None:
        self.config = config

        from app.core.db import DatabaseAccessor

        self.db = DatabaseAccessor(self)
        self.object_storage = ObjectStorageService(config.object_storage)

        from app.events.accessor import EventAccessor
        from app.ingest.accessor import OrganizerIngestAccessor
        from app.participation_applications.accessor import (
            ParticipationApplicationAccessor,
        )
        from app.roles.accessor import RoleAccessor
        from app.skills.accessor import SkillAccessor
        from app.teams.accessor import TeamAccessor
        from app.users.accessor import UserAccessor

        self.users = UserAccessor(self)
        self.roles = RoleAccessor(self)
        self.skills = SkillAccessor(self)
        self.teams = TeamAccessor(self)
        self.events = EventAccessor(self)
        self.participation_applications = ParticipationApplicationAccessor(self)
        self.organizer_ingest = OrganizerIngestAccessor(self)
