import asyncio
import logging
from datetime import datetime

from telegram.ext import Application

from config import settings
from handlers import register_handlers
from utils import ensure_log_directory


def configure_logging() -> None:
    """Configure application-wide logging."""
    ensure_log_directory()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(settings.log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.INFO)


def _format_local_time(dt: datetime | None = None) -> str:
    """Format local time as: 19 Jul 2026 • 11:45 PM."""
    now = dt or datetime.now()
    return f"{now.strftime('%d %b %Y')} • {now.strftime('%I:%M %p')}"


async def _send_startup_notification(application: Application) -> None:
    """Send startup notification to order group after bot starts."""
    startup_message = (
        "🤖 Telegram Order Bot Online\n\n"
        "✅ Status: Running\n\n"
        f"🕒 {_format_local_time()}"
    )
    await application.bot.send_message(
        chat_id=settings.order_group_id,
        text=startup_message,
    )


async def run_bot() -> None:
    """Build and run the Telegram bot."""
    configure_logging()
    logger = logging.getLogger(__name__)

    application = Application.builder().token(settings.bot_token).build()
    register_handlers(application)

    logger.info("Bot started")
    logger.info("Forward destination ORDER_GROUP_ID=%s", settings.order_group_id)

    await application.initialize()
    await application.start()
    if application.updater is None:
        raise RuntimeError("Application updater is not available.")

    await _send_startup_notification(application)
    await application.updater.start_polling(allowed_updates=["message"])

    logger.info("Bot started successfully and monitoring messages...")

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutdown signal received. Stopping bot...")
    finally:
        if application.updater is not None:
            await application.updater.stop()
        await application.stop()
        await application.shutdown()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(run_bot())
