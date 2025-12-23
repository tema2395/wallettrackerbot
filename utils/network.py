"""
Сетевые утилиты: простое кэширование и ограничение запросов
"""
from __future__ import annotations

import asyncio
import time
from typing import Any, Optional


class TTLCache:
    """Простой in-memory кэш с TTL"""

    def __init__(self, ttl_seconds: int):
        self._ttl_seconds = ttl_seconds
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        stored_at, value = item
        if time.monotonic() - stored_at > self._ttl_seconds:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.monotonic(), value)


class AsyncRateLimiter:
    """Минимальный интервал между запросами"""

    def __init__(self, min_interval_seconds: float):
        self._min_interval_seconds = min_interval_seconds
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def wait(self) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_call
            if elapsed < self._min_interval_seconds:
                await asyncio.sleep(self._min_interval_seconds - elapsed)
            self._last_call = time.monotonic()
