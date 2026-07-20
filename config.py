from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


def _get_ignored_user_ids() -> tuple[int, ...]:
    value = os.getenv("IGNORED_USER_IDS", "").strip()
    if not value:
        return ()

    try:
        return tuple(int(user_id.strip()) for user_id in value.split(",") if user_id.strip())
    except ValueError as exc:
        raise ValueError("IGNORED_USER_IDS must be a comma-separated list of integers") from exc


IGNORED_USER_IDS = _get_ignored_user_ids()


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    bot_token: str
    order_group_id: int
    ignored_user_ids: tuple[int, ...]
    log_file: str = "logs/bot.log"



def _get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


settings = Settings(
    bot_token=_get_required_env("BOT_TOKEN"),
    order_group_id=int(os.getenv("ORDER_GROUP_ID", "-1004406625020")),
    ignored_user_ids=IGNORED_USER_IDS,
)
