from __future__ import annotations

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update superuser from environment variables."

    def handle(self, *args: object, **kwargs: object) -> None:
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Skipped superuser bootstrap: DJANGO_SUPERUSER_USERNAME/PASSWORD is empty.",
                ),
            )
            return

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        changed_fields: list[str] = []

        if user.email != email:
            user.email = email
            changed_fields.append("email")

        if not user.is_staff:
            user.is_staff = True
            changed_fields.append("is_staff")

        if not user.is_superuser:
            user.is_superuser = True
            changed_fields.append("is_superuser")

        user.set_password(password)
        changed_fields.append("password")
        user.save(update_fields=changed_fields)

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Superuser '{username}' created."),
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"Superuser '{username}' updated."),
        )
