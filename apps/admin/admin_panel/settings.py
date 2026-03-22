from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _split_csv(value: str | None, fallback: list[str]) -> list[str]:
    if not value:
        return fallback
    return [item.strip() for item in value.split(",") if item.strip()]


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "CHANGE_THIS_DJANGO_SECRET")
DEBUG = _to_bool(os.getenv("DJANGO_DEBUG"), False)
ALLOWED_HOSTS = _split_csv(
    os.getenv("DJANGO_ALLOWED_HOSTS"),
    ["localhost", "127.0.0.1", "admin"],
)
CSRF_TRUSTED_ORIGINS = _split_csv(
    os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS"),
    ["http://localhost:8010", "http://127.0.0.1:8010"],
)

INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "backoffice",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "admin_panel.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "admin_panel.wsgi.application"
ASGI_APPLICATION = "admin_panel.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("APP_DB__NAME", "postgres"),
        "USER": os.getenv("APP_DB__USER", "postgres"),
        "PASSWORD": os.getenv("APP_DB__PASSWORD", "postgres"),
        "HOST": os.getenv("APP_DB__HOST", "localhost"),
        "PORT": int(os.getenv("APP_DB__PORT", "5432")),
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
]

LANGUAGE_CODE = "ru"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

UNFOLD = {
    "SITE_TITLE": "Idea Code Админка",
    "SITE_HEADER": "Idea Code Админка",
    "SITE_SUBHEADER": "Панель модерации",
    "SITE_SYMBOL": "admin_panel_settings",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Модерация",
                "separator": True,
                "items": [
                    {
                        "title": "Заявки на участие",
                        "icon": "assignment",
                        "link": "admin:backoffice_participationapplication_changelist",
                    },
                    {
                        "title": "События",
                        "icon": "event",
                        "link": "admin:backoffice_event_changelist",
                    },
                ],
            },
            {
                "title": "Справочники",
                "separator": True,
                "items": [
                    {
                        "title": "Роли",
                        "icon": "badge",
                        "link": "admin:backoffice_role_changelist",
                    },
                    {
                        "title": "Навыки",
                        "icon": "psychology",
                        "link": "admin:backoffice_skill_changelist",
                    },
                ],
            },
            {
                "title": "Интеграции",
                "separator": True,
                "items": [
                    {
                        "title": "API-токены организаторов",
                        "icon": "key",
                        "link": "admin:backoffice_organizerapitoken_changelist",
                    },
                ],
            },
            {
                "title": "Только просмотр",
                "separator": True,
                "items": [
                    {
                        "title": "Пользователи",
                        "icon": "group",
                        "link": "admin:backoffice_user_changelist",
                    },
                    {
                        "title": "Команды",
                        "icon": "groups",
                        "link": "admin:backoffice_team_changelist",
                    },
                    {
                        "title": "Рейтинги событий",
                        "icon": "workspace_premium",
                        "link": "admin:backoffice_admineventrating_changelist",
                    },
                    {
                        "title": "Telegram-аккаунты",
                        "icon": "send",
                        "link": "admin:backoffice_telegramidentity_changelist",
                    },
                ],
            },
        ],
    },
}
