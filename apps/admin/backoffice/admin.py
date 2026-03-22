from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib import admin, messages
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from backoffice.models import (
    AdminEventRating,
    Event,
    OrganizerAPIToken,
    ParticipationApplication,
    Role,
    Skill,
    Team,
    TelegramIdentity,
    User,
)

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest

TOKEN_HASH_VISIBLE_LENGTH = 16


def _status_badge(label: str, color: str) -> str:
    return format_html(
        (
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:999px;font-weight:600;">{}</span>'
        ),
        color,
        label,
    )


class ReadOnlyAdmin(ModelAdmin):
    actions: tuple[Any, ...] = ()

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(
        self,
        request: HttpRequest,
        obj: Any | None = None,
    ) -> bool:
        return False

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: Any | None = None,
    ) -> bool:
        return False


@admin.register(User)
class UserAdmin(ReadOnlyAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "activated",
        "open_to_teamup",
        "created_at",
        "updated_at",
    )
    list_filter = ("activated", "open_to_teamup", "roles", "skills")
    search_fields = ("username", "email", "name", "location")
    ordering = ("id",)


@admin.register(Team)
class TeamAdmin(ReadOnlyAdmin):
    list_display = ("id", "name", "external_id", "member_count", "updated_at")
    search_fields = ("name", "external_id", "description")
    ordering = ("name",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Team]:
        return super().get_queryset(request).prefetch_related("users")

    @admin.display(description="Members")
    def member_count(self, obj: Team) -> int:
        return obj.users.count()


@admin.register(TelegramIdentity)
class TelegramIdentityAdmin(ReadOnlyAdmin):
    list_display = (
        "id",
        "telegram_user_id",
        "username",
        "first_name",
        "last_name",
        "auth_date",
    )
    search_fields = ("=telegram_user_id", "username", "first_name", "last_name")
    list_filter = ("auth_date",)
    autocomplete_fields = ("user",)


@admin.register(AdminEventRating)
class AdminEventRatingAdmin(ReadOnlyAdmin):
    list_display = ("event_id", "user_id", "team_id", "status", "place", "awarded_at")
    list_filter = ("status", "awarded_at")
    search_fields = ("=event_id", "=user_id", "=team_id")
    autocomplete_fields = ("event", "user", "team")
    ordering = ("-awarded_at",)


@admin.register(Event)
class EventAdmin(ModelAdmin):
    list_display = (
        "id",
        "title",
        "external_id",
        "date",
        "verify_badge",
        "created_at",
        "updated_at",
    )
    search_fields = ("title", "description", "external_id")
    list_filter = ("is_verify", "date", "created_at")
    readonly_fields = ("created_at", "updated_at")
    actions = ("mark_verified", "mark_unverified")
    ordering = ("-date",)

    @admin.display(description="Verification")
    def verify_badge(self, obj: Event) -> str:
        if obj.is_verify:
            return _status_badge("Verified", "#16a34a")
        return _status_badge("Not verified", "#6b7280")

    @admin.action(description="Mark selected events as verified")
    def mark_verified(
        self,
        request: HttpRequest,
        queryset: QuerySet[Event],
    ) -> None:
        updated = queryset.exclude(is_verify=True).update(is_verify=True)
        self.message_user(
            request,
            f"Marked {updated} event(s) as verified.",
            level=messages.SUCCESS,
        )

    @admin.action(description="Mark selected events as not verified")
    def mark_unverified(
        self,
        request: HttpRequest,
        queryset: QuerySet[Event],
    ) -> None:
        updated = queryset.exclude(is_verify=False).update(is_verify=False)
        self.message_user(
            request,
            f"Marked {updated} event(s) as not verified.",
            level=messages.SUCCESS,
        )


@admin.register(ParticipationApplication)
class ParticipationApplicationAdmin(ModelAdmin):
    list_display = (
        "id",
        "applicant",
        "event",
        "status_badge",
        "preferred_team_format",
        "desired_role",
        "created_at",
    )
    list_filter = ("status", "preferred_team_format", "event", "created_at")
    search_fields = (
        "=id",
        "applicant__username",
        "applicant__email",
        "event__title",
        "desired_role",
        "comment",
    )
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("applicant", "event")
    list_select_related = ("applicant", "event")
    actions = ("approve_selected", "reject_selected", "mark_pending")
    ordering = ("-created_at",)

    @admin.display(description="Status")
    def status_badge(self, obj: ParticipationApplication) -> str:
        if obj.status == ParticipationApplication.Status.APPROVED:
            return _status_badge("Approved", "#16a34a")
        if obj.status == ParticipationApplication.Status.REJECTED:
            return _status_badge("Rejected", "#dc2626")
        return _status_badge("Pending", "#f59e0b")

    @admin.action(description="Approve selected applications")
    def approve_selected(
        self,
        request: HttpRequest,
        queryset: QuerySet[ParticipationApplication],
    ) -> None:
        updated = queryset.exclude(
            status=ParticipationApplication.Status.APPROVED,
        ).update(status=ParticipationApplication.Status.APPROVED)
        self.message_user(
            request,
            f"Approved {updated} application(s).",
            level=messages.SUCCESS,
        )

    @admin.action(description="Reject selected applications")
    def reject_selected(
        self,
        request: HttpRequest,
        queryset: QuerySet[ParticipationApplication],
    ) -> None:
        updated = queryset.exclude(
            status=ParticipationApplication.Status.REJECTED,
        ).update(status=ParticipationApplication.Status.REJECTED)
        self.message_user(
            request,
            f"Rejected {updated} application(s).",
            level=messages.SUCCESS,
        )

    @admin.action(description="Move selected applications to pending")
    def mark_pending(
        self,
        request: HttpRequest,
        queryset: QuerySet[ParticipationApplication],
    ) -> None:
        updated = queryset.exclude(
            status=ParticipationApplication.Status.PENDING,
        ).update(status=ParticipationApplication.Status.PENDING)
        self.message_user(
            request,
            f"Moved {updated} application(s) to pending.",
            level=messages.SUCCESS,
        )


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Skill)
class SkillAdmin(ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(OrganizerAPIToken)
class OrganizerAPITokenAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "token_hash_short",
        "active_badge",
        "last_used_at",
        "updated_at",
    )
    search_fields = ("name", "token_hash")
    list_filter = ("is_active", "last_used_at", "updated_at")
    readonly_fields = ("created_at", "updated_at", "last_used_at")
    actions = ("activate_selected", "deactivate_selected")
    ordering = ("name",)

    @admin.display(description="Token hash")
    def token_hash_short(self, obj: OrganizerAPIToken) -> str:
        if len(obj.token_hash) <= TOKEN_HASH_VISIBLE_LENGTH:
            return obj.token_hash
        return f"{obj.token_hash[:8]}...{obj.token_hash[-8:]}"

    @admin.display(description="Active")
    def active_badge(self, obj: OrganizerAPIToken) -> str:
        if obj.is_active:
            return _status_badge("Active", "#16a34a")
        return _status_badge("Inactive", "#6b7280")

    @admin.action(description="Activate selected tokens")
    def activate_selected(
        self,
        request: HttpRequest,
        queryset: QuerySet[OrganizerAPIToken],
    ) -> None:
        updated = queryset.exclude(is_active=True).update(is_active=True)
        self.message_user(
            request,
            f"Activated {updated} token(s).",
            level=messages.SUCCESS,
        )

    @admin.action(description="Deactivate selected tokens")
    def deactivate_selected(
        self,
        request: HttpRequest,
        queryset: QuerySet[OrganizerAPIToken],
    ) -> None:
        updated = queryset.exclude(is_active=False).update(is_active=False)
        self.message_user(
            request,
            f"Deactivated {updated} token(s).",
            level=messages.SUCCESS,
        )
