from telegram import Message

from keywords import KEYWORDS


def _normalize_content(value: str | None) -> str:
    """Normalize message content for case-insensitive keyword checks."""
    return (value or "").lower().strip()


def _find_matched_keyword(content: str) -> str:
    """Return the first matched keyword from content, or empty string if none."""
    for keyword in KEYWORDS:
        if keyword in content:
            return keyword
    return ""


def detect_order_content(text: str | None, caption: str | None) -> tuple[bool, str]:
    """
    Unit-test-friendly detector that checks both text and caption.

    Returns:
        tuple[bool, str]: (detected, matched_keyword)
    """
    normalized_text = _normalize_content(text)
    normalized_caption = _normalize_content(caption)

    if normalized_text:
        matched_keyword = _find_matched_keyword(normalized_text)
        if matched_keyword:
            return True, matched_keyword

    if normalized_caption:
        matched_keyword = _find_matched_keyword(normalized_caption)
        if matched_keyword:
            return True, matched_keyword

    return False, ""


def message_contains_keywords(message: Message) -> tuple[bool, str]:
    """
    Backward-compatible wrapper around detect_order_content.

    Returns:
        tuple[bool, str]: (detected, matched_keyword)
    """
    return detect_order_content(message.text, message.caption)
