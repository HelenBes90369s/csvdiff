"""Run-level deduplication guard: prevents the same pair of CSV files
from being diffed twice within a configurable time window."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


class DedupeRunError(Exception):
    """Raised when a deduplication-run violation occurs."""


@dataclass
class DedupeRunOptions:
    window_seconds: float = 60.0
    max_entries: int = 256

    def __post_init__(self) -> None:
        if self.window_seconds <= 0:
            raise DedupeRunError("window_seconds must be positive")
        if self.max_entries < 1:
            raise DedupeRunError("max_entries must be at least 1")


@dataclass
class DedupeRunState:
    options: DedupeRunOptions
    _seen: Dict[str, float] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------
    def _make_key(self, path_a: str, path_b: str, keys: Tuple[str, ...]) -> str:
        raw = f"{path_a}|{path_b}|{'&'.join(sorted(keys))}"
        return hashlib.sha1(raw.encode()).hexdigest()

    def _evict_expired(self, now: float) -> None:
        cutoff = now - self.options.window_seconds
        expired = [k for k, ts in self._seen.items() if ts < cutoff]
        for k in expired:
            del self._seen[k]

    def _evict_oldest(self) -> None:
        if not self._seen:
            return
        oldest = min(self._seen, key=lambda k: self._seen[k])
        del self._seen[oldest]

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def is_duplicate(self, path_a: str, path_b: str, keys: Tuple[str, ...]) -> bool:
        """Return True if this run was already recorded within the window."""
        now = time.monotonic()
        self._evict_expired(now)
        key = self._make_key(path_a, path_b, keys)
        return key in self._seen

    def record(self, path_a: str, path_b: str, keys: Tuple[str, ...]) -> None:
        """Record a run so future calls within the window are flagged."""
        now = time.monotonic()
        self._evict_expired(now)
        while len(self._seen) >= self.options.max_entries:
            self._evict_oldest()
        key = self._make_key(path_a, path_b, keys)
        self._seen[key] = now

    def clear(self) -> None:
        """Reset all recorded runs."""
        self._seen.clear()

    @property
    def entry_count(self) -> int:
        return len(self._seen)
