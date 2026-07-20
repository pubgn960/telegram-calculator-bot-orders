from dataclasses import dataclass, field
import os

from dotenv import load_dotenv


load_dotenv()


def _parse_ignored_user_ids() -> frozenset[int]:
    raw = os.getenv("IGNORED_USER_IDS", "").strip()
    if not raw:
        return frozenset()
    return frozenset(int(uid.strip()) for uid in raw.split(",") if uid.strip())


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    bot_token: str
    order_group_id: int
    ignored_user_ids: frozenset[int] = field(default_factory=frozenset)
    log_file: str = "logs/bot.log"


def _get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


settings = Settings(
    bot_token=_get_required_env("BOT_TOKEN"),
    order_group_id=int(os.getenv("ORDER_GROUP_ID", "-1004406625020")),
    ignored_user_ids=_parse_ignored_user_ids(),
)
