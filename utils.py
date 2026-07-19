from collections import deque
from pathlib import Path
from typing import Deque


def ensure_log_directory() -> None:
    """Ensure logs directory exists."""
    Path("logs").mkdir(parents=True, exist_ok=True)


class ForwardedMessageCache:
    """
    In-memory duplicate forwarding prevention cache using (chat_id, message_id).
    """

    def __init__(self, max_size: int = 20000) -> None:
        self.max_size = max_size
        self._set: set[tuple[int, int]] = set()
        self._queue: Deque[tuple[int, int]] = deque()

    def exists(self, key: tuple[int, int]) -> bool:
        return key in self._set

    def add(self, key: tuple[int, int]) -> None:
        if key in self._set:
            return

        self._set.add(key)
        self._queue.append(key)

        while len(self._queue) > self.max_size:
            old_key = self._queue.popleft()
            self._set.discard(old_key)
