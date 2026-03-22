from app.core.config import Config


class Store:
    def __init__(self, *, config: Config) -> None:
        self.config = config

        from app.core.db import DatabaseAccessor

        self.db = DatabaseAccessor(self)

        from app.events.accessor import EventAccessor
        from app.ingest.accessor import OrganizerIngestAccessor
        from app.roles.accessor import RoleAccessor
        from app.skills.accessor import SkillAccessor
        from app.teams.accessor import TeamAccessor
        from app.users.accessor import UserAccessor

        self.users = UserAccessor(self)
        self.roles = RoleAccessor(self)
        self.skills = SkillAccessor(self)
        self.teams = TeamAccessor(self)
        self.events = EventAccessor(self)
        self.organizer_ingest = OrganizerIngestAccessor(self)
