from __future__ import annotations

from django.db import models


class UnmanagedModel(models.Model):
    class Meta:
        abstract = True
        managed = False


class Role(UnmanagedModel):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta(UnmanagedModel.Meta):
        db_table = "roles"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Skill(UnmanagedModel):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta(UnmanagedModel.Meta):
        db_table = "skills"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class User(UnmanagedModel):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=100, default="", blank=True)
    avatar = models.URLField(max_length=2048, null=True, blank=True)
    description = models.CharField(max_length=1000, default="", blank=True)
    location = models.CharField(max_length=100, default="", blank=True)
    links = models.JSONField(default=list, blank=True)
    activated = models.BooleanField(default=False)
    open_to_teamup = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    roles = models.ManyToManyField("Role", through="UserRole", related_name="users")
    skills = models.ManyToManyField("Skill", through="UserSkill", related_name="users")

    class Meta(UnmanagedModel.Meta):
        db_table = "users"
        ordering = ("id",)

    def __str__(self) -> str:
        return self.username


class UserRole(UnmanagedModel):
    pk = models.CompositePrimaryKey("user", "role")
    user = models.ForeignKey("User", models.DO_NOTHING, db_column="user_id")
    role = models.ForeignKey("Role", models.DO_NOTHING, db_column="role_id")

    class Meta(UnmanagedModel.Meta):
        db_table = "user_roles"
        unique_together = (("user", "role"),)


class UserSkill(UnmanagedModel):
    pk = models.CompositePrimaryKey("user", "skill")
    user = models.ForeignKey("User", models.DO_NOTHING, db_column="user_id")
    skill = models.ForeignKey("Skill", models.DO_NOTHING, db_column="skill_id")

    class Meta(UnmanagedModel.Meta):
        db_table = "user_skills"
        unique_together = (("user", "skill"),)


class TelegramIdentity(UnmanagedModel):
    id = models.IntegerField(primary_key=True)
    user = models.OneToOneField("User", models.DO_NOTHING, db_column="user_id")
    telegram_user_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    photo_url = models.URLField(max_length=2048, null=True, blank=True)
    auth_date = models.DateTimeField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta(UnmanagedModel.Meta):
        db_table = "telegram_identities"
        ordering = ("-auth_date",)

    def __str__(self) -> str:
        return f"{self.first_name} ({self.telegram_user_id})"


class Team(UnmanagedModel):
    id = models.IntegerField(primary_key=True)
    external_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=1000, default="", blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    users = models.ManyToManyField("User", through="TeamUser", related_name="teams")

    class Meta(UnmanagedModel.Meta):
        db_table = "teams"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class TeamUser(UnmanagedModel):
    pk = models.CompositePrimaryKey("team", "user")
    team = models.ForeignKey("Team", models.DO_NOTHING, db_column="team_id")
    user = models.ForeignKey("User", models.DO_NOTHING, db_column="user_id")

    class Meta(UnmanagedModel.Meta):
        db_table = "team_users"
        unique_together = (("team", "user"),)


class Event(UnmanagedModel):
    id = models.IntegerField(primary_key=True)
    external_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, default="", blank=True)
    date = models.DateTimeField()
    cover = models.URLField(max_length=2048, null=True, blank=True)
    is_verify = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta(UnmanagedModel.Meta):
        db_table = "events"
        ordering = ("-date",)

    def __str__(self) -> str:
        return self.title


class ParticipationApplication(UnmanagedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    class PreferredTeamFormat(models.TextChoices):
        SOLO = "solo", "Solo"
        TEAM = "team", "Team"

    id = models.IntegerField(primary_key=True)
    applicant = models.ForeignKey(
        "User",
        models.DO_NOTHING,
        db_column="applicant_user_id",
        related_name="participation_applications",
    )
    event = models.ForeignKey(
        "Event",
        models.DO_NOTHING,
        db_column="event_id",
        related_name="participation_applications",
    )
    comment = models.CharField(max_length=1000, default="", blank=True)
    desired_role = models.CharField(max_length=100, default="", blank=True)
    preferred_team_format = models.CharField(
        max_length=20,
        choices=PreferredTeamFormat.choices,
        default=PreferredTeamFormat.TEAM,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    skills = models.ManyToManyField(
        "Skill",
        through="ParticipationApplicationSkill",
        related_name="applications",
    )
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta(UnmanagedModel.Meta):
        db_table = "participation_applications"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.applicant} -> {self.event} ({self.status})"


class ParticipationApplicationSkill(UnmanagedModel):
    pk = models.CompositePrimaryKey("application", "skill")
    application = models.ForeignKey(
        "ParticipationApplication",
        models.DO_NOTHING,
        db_column="application_id",
    )
    skill = models.ForeignKey("Skill", models.DO_NOTHING, db_column="skill_id")

    class Meta(UnmanagedModel.Meta):
        db_table = "participation_application_skills"
        unique_together = (("application", "skill"),)


class OrganizerAPIToken(UnmanagedModel):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    token_hash = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta(UnmanagedModel.Meta):
        db_table = "organizer_api_tokens"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class AdminEventRating(UnmanagedModel):
    class Status(models.TextChoices):
        WINNER = "winner", "Winner"
        PRIZE_WINNER = "prize_winner", "Prize winner"
        PARTICIPANT = "participant", "Participant"

    id = models.CharField(max_length=64, primary_key=True)
    event = models.ForeignKey("Event", models.DO_NOTHING, db_column="event_id")
    user = models.ForeignKey("User", models.DO_NOTHING, db_column="user_id")
    status = models.CharField(max_length=20, choices=Status.choices)
    place = models.IntegerField(null=True, blank=True)
    team = models.ForeignKey(
        "Team",
        models.DO_NOTHING,
        db_column="team_id",
        null=True,
        blank=True,
    )
    awarded_at = models.DateTimeField()

    class Meta(UnmanagedModel.Meta):
        db_table = "admin_event_ratings"
        ordering = ("-awarded_at",)

    def __str__(self) -> str:
        return f"Event #{self.event_id} - User #{self.user_id}"
