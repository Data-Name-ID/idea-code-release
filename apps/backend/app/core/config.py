from datetime import timedelta
from typing import Literal

import msgspec
from dynaconf import Dynaconf
from sqlalchemy.engine.url import URL


class StaticConfig:
    SHORT_STR_LENGTH = 20  # Коды, статусы, идентификаторы
    NAME_STR_LENGTH = 100  # Имена, логины, названия, заголовки, теги
    DESCRIPTION_STR_LENGTH = 500  # Краткие описания, аннотации, комментарии
    LONG_STR_LENGTH = 1000  # Длинные тексты, описания, аннотации
    URL_STR_LENGTH = 2048  # Ссылки, адреса, пути
    CREDENTIALS_STR_LENGTH = 255  # Email-адреса, пароли


class DatabaseConfig(msgspec.Struct, kw_only=True, frozen=True):
    user: str | None = "postgres"
    password: str | None = "postgres"  # noqa: S105
    host: str = "localhost"
    port: int = 5432
    name: str = "postgres"

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    @property
    def url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        )


class JWTConfig(msgspec.Struct, kw_only=True, frozen=True):
    token_secret: str
    token_expiration_minutes: int = 15
    refresh_token_secret: str | None = None
    refresh_token_expiration_minutes: int = 60 * 24 * 30  # 30 days

    @property
    def token_expiration(self) -> timedelta:
        return timedelta(minutes=self.token_expiration_minutes)

    @property
    def refresh_token_expiration(self) -> timedelta:
        return timedelta(minutes=self.refresh_token_expiration_minutes)

    @property
    def effective_refresh_secret(self) -> str:
        return self.refresh_token_secret or self.token_secret


class TelegramConfig(msgspec.Struct, kw_only=True, frozen=True):
    bot_token: str = ""
    bot_username: str = ""
    auth_max_age_seconds: int = 15 * 60


class CookieConfig(msgspec.Struct, kw_only=True, frozen=True):
    key: str = "access_token"
    path: str = "/"
    domain: str | None = None
    secure: bool = False
    samesite: Literal["lax", "strict", "none"] = "lax"


class SecurityConfig(msgspec.Struct, kw_only=True, frozen=True):
    cors_allowed_origins: list[str] = msgspec.field(
        default_factory=lambda: [
            "http://localhost",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
    )
    cors_allow_credentials: bool = True
    jwt: JWTConfig
    telegram: TelegramConfig = msgspec.field(default_factory=TelegramConfig)
    cookie: CookieConfig = msgspec.field(default_factory=CookieConfig)


class ObjectStorageConfig(msgspec.Struct, kw_only=True, frozen=True):
    endpoint: str = "localhost:9000"
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"  # noqa: S105
    secure: bool = False
    bucket: str = "avatars"
    public_base_url: str = "http://localhost:9000"
    max_upload_size_mb: int = 5


class Config(msgspec.Struct, kw_only=True, frozen=True):
    db: DatabaseConfig
    security: SecurityConfig
    object_storage: ObjectStorageConfig = msgspec.field(
        default_factory=ObjectStorageConfig,
    )


def _lower_keys(data: object) -> object:
    if isinstance(data, dict):
        return {str(key).lower(): _lower_keys(value) for key, value in data.items()}
    if isinstance(data, list):
        return [_lower_keys(item) for item in data]
    return data


def create_config() -> Config:
    settings = Dynaconf(
        settings_files=[".secrets.yaml", ".env"],
        envvar_prefix="APP",
        load_dotenv=True,
        merge_enabled=True,
    )
    config_raw = _lower_keys(settings.as_dict())
    if isinstance(config_raw, dict):
        config_raw.pop("load_dotenv", None)
    return msgspec.convert(config_raw, type=Config)
