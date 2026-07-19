import logging
from datetime import datetime

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from config import settings
from detector import message_contains_keywords
from utils import ForwardedMessageCache


logger = logging.getLogger(__name__)
cache = ForwardedMessageCache()


def _format_local_time(dt: datetime | None = None) -> str:
    """Format local time as: 19 Jul 2026 • 11:45 PM."""
    now = dt or datetime.now()
    return f"{now.strftime('%d %b %Y')} • {now.strftime('%I:%M %p')}"


def _build_order_info_message(update: Update) -> str:
    """Build the order information message sent before forwarding."""
    chat = update.effective_chat
    user = update.effective_user

    group_title = chat.title if chat and chat.title else "Unknown Group"
    first_name = user.first_name if user and user.first_name else "Unknown"
    username = f"@{user.username}" if user and user.username else ""
    current_local_time = _format_local_time()

    customer_details = first_name if not username else f"{first_name}\n{username}"

    return (
        "📥 NEW ORDER\n\n"
        f"👥 Group: {group_title}\n\n"
        "👤 Customer:\n"
        f"{customer_details}\n\n"
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

        logger.info("New order detected chat_id=%s message_id=%s", chat.id, message.message_id)

        if not any([message.text, message.photo, message.video, message.document, message.caption]):
            return

        key = (chat.id, message.message_id)
        if cache.exists(key):
            logger.info("Duplicate skipped chat_id=%s message_id=%s", chat.id, message.message_id)
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

        try:
            await message.set_reaction("👍")
        except TelegramError:
            logger.exception(
                "Reaction failed chat_id=%s chat_type=%s message_id=%s",
                chat.id,
                chat.type,
                message.message_id,
            )

        cache.add(key)
        logger.info(
            "Forward successful chat_id=%s message_id=%s -> order_group_id=%s",
            chat.id,
            message.message_id,
            settings.order_group_id,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "Forward failed chat_id=%s message_id=%s error=%s",
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
