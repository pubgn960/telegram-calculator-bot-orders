import asyncio
import logging
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


async def run_bot() -> None:
    """Build and run the Telegram bot."""
    configure_logging()
    logger = logging.getLogger(__name__)

    application = Application.builder().token(settings.bot_token).build()
    register_handlers(application)

    logger.info("Starting Telegram Order Detection Bot...")
    logger.info("Forward destination ORDER_GROUP_ID=%s", settings.order_group_id)

    await application.initialize()
    await application.start()
    if application.updater is None:
        raise RuntimeError("Application updater is not available.")

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
