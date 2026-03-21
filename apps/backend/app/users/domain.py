from msgspec import Struct


class UserAuth(Struct, kw_only=True, frozen=True):
    id: int


class TelegramIdentityInput(Struct, kw_only=True, frozen=True):
    telegram_user_id: int
    username: str | None
    first_name: str
    last_name: str | None
    photo_url: str | None


class AuthUser(Struct, kw_only=True, frozen=True):
    id: int
    telegram_user_id: int
    username: str | None
    first_name: str
    last_name: str | None
    photo_url: str | None


class LinkData(Struct, kw_only=True, frozen=True):
    url: str
    label: str

    def to_dict(self) -> dict[str, str]:
        return {"url": self.url, "label": self.label}
