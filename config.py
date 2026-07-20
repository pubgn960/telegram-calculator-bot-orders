from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


def _get_ignored_user_ids() -> frozenset[int]:
    value = os.getenv("IGNORED_USER_IDS", "").strip()
    if not value:
        return frozenset()

    ignored_user_ids: list[int] = []
    for raw_user_id in value.split(","):
        user_id = raw_user_id.strip()
        if not user_id:
            continue
        try:
            ignored_user_ids.append(int(user_id))
        except ValueError as exc:
            raise ValueError(f"IGNORED_USER_IDS contains invalid integer: {user_id}") from exc

    return frozenset(ignored_user_ids)


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    bot_token: str
    order_group_id: int
    ignored_user_ids: frozenset[int]
    log_file: str = "logs/bot.log"



def _get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


settings = Settings(
    bot_token=_get_required_env("BOT_TOKEN"),
    order_group_id=int(os.getenv("ORDER_GROUP_ID", "-1004406625020")),
    ignored_user_ids=_get_ignored_user_ids(),
)
