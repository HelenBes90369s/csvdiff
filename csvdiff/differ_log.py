"""Structured logging for diff operations."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from csvdiff.differ import DiffResult


class LogError(Exception):
    pass


@dataclass
class LogOptions:
    level: str = "INFO"
    include_stats: bool = True
    include_timestamp: bool = True

    def __post_init__(self) -> None:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR"}
        if self.level not in valid:
            raise LogError(f"level must be one of {valid}, got {self.level!r}")


@dataclass
class LogEntry:
    level: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"level": self.level, "message": self.message}
        if self.timestamp is not None:
            d["timestamp"] = self.timestamp
        if self.data:
            d["data"] = self.data
        return d

    def as_json(self) -> str:
        return json.dumps(self.as_dict())


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def build_log_entry(
    result: DiffResult,
    message: str,
    options: Optional[LogOptions] = None,
) -> LogEntry:
    if result is None:
        raise LogError("result must not be None")
    if not message or not message.strip():
        raise LogError("message must not be blank")
    opts = options or LogOptions()
    data: Dict[str, Any] = {}
    if opts.include_stats:
        data["added"] = len(result.added)
        data["removed"] = len(result.removed)
        data["changed"] = len(result.changed)
    ts = _now_iso() if opts.include_timestamp else None
    return LogEntry(level=opts.level, message=message.strip(), data=data, timestamp=ts)


def emit_log_entries(
    entries: List[LogEntry],
    logger: Optional[logging.Logger] = None,
) -> None:
    if logger is None:
        logger = logging.getLogger("csvdiff")
    for entry in entries:
        lvl = getattr(logging, entry.level, logging.INFO)
        logger.log(lvl, entry.as_json())
