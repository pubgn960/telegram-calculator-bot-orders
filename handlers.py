import logging

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from config import settings
from detector import message_contains_keywords
from utils import ForwardedMessageCache


logger = logging.getLogger(__name__)
cache = ForwardedMessageCache()


async def monitor_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Monitor all incoming group/supergroup messages and forward matched messages.
    """
    message = update.effective_message
    chat = update.effective_chat

    if message is None or chat is None:
        return

    if chat.type not in {"group", "supergroup"}:
        return

    try:
        matched, source = message_contains_keywords(message)
        if not matched:
            return

        logger.info(
            "Detected order keyword in %s chat_id=%s message_id=%s",
            source,
            chat.id,
            message.message_id,
        )

        key = (chat.id, message.message_id)
        if cache.exists(key):
            logger.info(
                "Duplicate detected, skipping forward chat_id=%s message_id=%s",
                chat.id,
                message.message_id,
            )
            return

        await context.bot.forward_message(
            chat_id=settings.order_group_id,
            from_chat_id=chat.id,
            message_id=message.message_id,
        )

        cache.add(key)
        logger.info(
            "Forwarded matched message chat_id=%s message_id=%s -> order_group_id=%s",
            chat.id,
            message.message_id,
            settings.order_group_id,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "Failed handling message chat_id=%s message_id=%s error=%s",
            chat.id,
            message.message_id,
            exc,
        )


def register_handlers(application: Application) -> None:
    """Register all bot handlers."""
    group_filter = filters.ChatType.GROUPS
    message_filter = filters.ALL & (~filters.StatusUpdate.ALL)
    application.add_handler(MessageHandler(group_filter & message_filter, monitor_messages))
