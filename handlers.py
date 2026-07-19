import logging
from datetime import datetime

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from config import settings
from detector import message_contains_keywords
from utils import ForwardedMessageCache


logger = logging.getLogger(__name__)
cache = ForwardedMessageCache()


def _build_order_info_message(update: Update) -> str:
    """Build the order information message sent before forwarding."""
    chat = update.effective_chat
    user = update.effective_user

    group_title = chat.title if chat and chat.title else "Unknown Group"
    first_name = user.first_name if user and user.first_name else "Unknown"
    username = f"@{user.username}" if user and user.username else ""
    current_local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    customer_lines = [first_name]
    if username:
        customer_lines.append(username)

    return (
        "📥 NEW ORDER\n\n"
        f"👥 Group: {group_title}\n\n"
        "👤 Customer:\n"
        f"{"\n".join(customer_lines)}\n\n"
        f"🕒 {current_local_time}\n\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )


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
        matched, _matched_keyword = message_contains_keywords(message)
        if not matched:
            return

        if not any([message.text, message.photo, message.video, message.document, message.caption]):
            return

        key = (chat.id, message.message_id)
        if cache.exists(key):
            logger.info(
                "Duplicate detected, skipping forward chat_id=%s message_id=%s",
                chat.id,
                message.message_id,
            )
            return

        info_message = _build_order_info_message(update)

        await context.bot.send_message(
            chat_id=settings.order_group_id,
            text=info_message,
        )

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
            "Failed forwarding order chat_id=%s message_id=%s error=%s",
            chat.id,
            message.message_id,
            exc,
        )


def register_handlers(application: Application) -> None:
    """Register all bot handlers."""
    group_filter = filters.ChatType.GROUPS
    supported_message_filter = (
        filters.TEXT
        | filters.PHOTO
        | filters.VIDEO
        | filters.Document.ALL
        | filters.CAPTION
    )
    message_filter = supported_message_filter & (~filters.StatusUpdate.ALL)
    application.add_handler(MessageHandler(group_filter & message_filter, monitor_messages))
