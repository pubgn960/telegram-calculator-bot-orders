import logging

from telegram import ReactionTypeEmoji, Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from config import settings
from detector import message_contains_keywords
from utils import ForwardedMessageCache


logger = logging.getLogger(__name__)
cache = ForwardedMessageCache()


async def monitor_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Ignore configured users (owner/admin)
    if (
        update.effective_user
        and update.effective_user.id in settings.ignored_user_ids
    ):
        logger.info(
            "Ignored message from user_id=%s",
            update.effective_user.id,
        )
        return

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

        await context.bot.forward_message(
            chat_id=settings.order_group_id,
            from_chat_id=chat.id,
            message_id=message.message_id,
        )

        # Try to add 👍 reaction if supported by PTB/Bot API
        try:
            if hasattr(context.bot, "set_message_reaction"):
                await context.bot.set_message_reaction(
                    chat_id=chat.id,
                    message_id=message.message_id,
                    reaction=[ReactionTypeEmoji("👍")],
                )
                logger.info(
                    "Reaction added chat_id=%s message_id=%s",
                    chat.id,
                    message.message_id,
                )
            else:
                logger.info("Message reactions are not supported by this PTB version.")
        except Exception as reaction_error:
            logger.warning("Could not add reaction: %s", reaction_error)

        cache.add(key)
        logger.info(
            "Forward successful chat_id=%s message_id=%s -> order_group_id=%s",
            chat.id,
            message.message_id,
            settings.order_group_id,
        )

    except Exception as exc:
        logger.exception(
            "Forward failed chat_id=%s message_id=%s error=%s",
            chat.id,
            message.message_id,
            exc,
        )


def register_handlers(application: Application) -> None:
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
