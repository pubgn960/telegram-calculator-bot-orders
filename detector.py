from telegram import Message

from keywords import KEYWORDS


def _normalize_content(value: str | None) -> str:
    return (value or "").lower().strip()


def _contains_keyword(content: str) -> bool:
    return any(keyword in content for keyword in KEYWORDS)


def message_contains_keywords(message: Message) -> tuple[bool, str]:
    """
    Check both message text and media captions for keyword matches.

    Returns:
        tuple[bool, str]: (matched, source) where source is 'text', 'caption', or ''.
    """
    text = _normalize_content(message.text)
    caption = _normalize_content(message.caption)

    if text and _contains_keyword(text):
        return True, "text"

    if caption and _contains_keyword(caption):
        return True, "caption"

    return False, ""
