from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    bot_token: str
    order_group_id: int
    log_file: str = "logs/bot.log"



def _get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


settings = Settings(
    bot_token=_get_required_env("BOT_TOKEN"),
    order_group_id=int(os.getenv("ORDER_GROUP_ID", "-1004406625020")),
)
