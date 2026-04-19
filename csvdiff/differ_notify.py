"""Notification dispatch after a diff completes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from csvdiff.differ import DiffResult


class NotifyError(Exception):
    """Raised for notification configuration or dispatch errors."""


@dataclass
class NotifyOptions:
    channels: List[str] = field(default_factory=lambda: ["log"])
    on_changes_only: bool = True
    min_changes: int = 1

    def __post_init__(self) -> None:
        valid = {"log", "stdout", "callback"}
        for ch in self.channels:
            if ch not in valid:
                raise NotifyError(f"Unknown channel: {ch!r}. Valid: {valid}")
        if not self.channels:
            raise NotifyError("channels must not be empty")
        if self.min_changes < 0:
            raise NotifyError("min_changes must be >= 0")


@dataclass
class NotifyPayload:
    added: int
    removed: int
    changed: int
    message: str

    @property
    def total(self) -> int:
        return self.added + self.removed + self.changed


def _build_payload(result: DiffResult) -> NotifyPayload:
    msg = (
        f"{len(result.added)} added, "
        f"{len(result.removed)} removed, "
        f"{len(result.changed)} changed"
    )
    return NotifyPayload(
        added=len(result.added),
        removed=len(result.removed),
        changed=len(result.changed),
        message=msg,
    )


def notify_diff(
    result: Optional[DiffResult],
    options: Optional[NotifyOptions] = None,
    callback: Optional[Callable[[NotifyPayload], None]] = None,
) -> Optional[NotifyPayload]:
    """Build and dispatch a notification payload for *result*.

    Returns the payload if dispatched, else None.
    """
    if result is None:
        raise NotifyError("result must not be None")
    opts = options or NotifyOptions()
    payload = _build_payload(result)

    if opts.on_changes_only and payload.total < opts.min_changes:
        return None

    for ch in opts.channels:
        if ch == "stdout":
            print(f"[csvdiff] {payload.message}")
        elif ch == "log":
            import logging
            logging.getLogger("csvdiff.notify").info(payload.message)
        elif ch == "callback":
            if callback is None:
                raise NotifyError("channel 'callback' requires a callback function")
            callback(payload)

    return payload
