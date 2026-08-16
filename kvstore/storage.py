import time
from dataclasses import dataclass

from kvstore.constants import StorageErrorMessage


@dataclass(slots=True)
class _Entry:
    value: str
    expires_at: float | None  # None = "без TTL" (ttl_seconds=0 в запросе)


class LRUTTLStore:
    def __init__(self, capacity: int = 10) -> None:
        if capacity <= 0:
            raise ValueError(
                StorageErrorMessage.invalid_capacity.format(
                    capacity=capacity
                )
            )
        self._capacity = capacity

    async def put(self, key: str, value: str, ttl_seconds: int) -> None:
        async with self._lock:
            expires_at = (
                None
                if ttl_seconds == 0
                else time.monotonic() + ttl_seconds
            )
            self._data[key] = _Entry(value=value, expires_at=expires_at)
            self._data.move_to_end(key)
            self._evict_if_over_capacity()

    async def get(self, key: str) -> str | None:
        async with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return None
            if self._is_expired(entry):
                del self._data[key]
                return None
            self._data.move_to_end(key)
            return entry.value

    async def delete(self, key: str) -> bool:
        async with self._lock:
            if key in self._data:
                del self._data[key]
                return True
            return False

    async def list_by_prefix(self, prefix: str) -> list[tuple[str, str]]:
        async with self._lock:
            result: list[tuple[str, str]] = []
            expired_keys: list[str] = []
            for key, entry in self._data.items():
                if self._is_expired(entry):
                    expired_keys.append(key)
                    continue
                if key.startswith(prefix):
                    result.append((key, entry.value))

            for key in expired_keys:
                del self._data[key]

            return result

    def _is_expired(self, entry: _Entry) -> bool:
        return (
            entry.expires_at is not None
            and time.monotonic() >= entry.expires_at
        )

    def _evict_if_over_capacity(self) -> None:
        while len(self._data) > self._capacity:
            self._data.popitem(last=False)
