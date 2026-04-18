"""Watch two CSV files and report when their diff changes."""
from __future__ import annotations

import time
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from csvdiff.differ import DiffResult


class WatchError(Exception):
    pass


@dataclass
class WatchOptions:
    interval: float = 2.0
    max_polls: Optional[int] = None

    def __post_init__(self) -> None:
        if self.interval <= 0:
            raise WatchError("interval must be positive")
        if self.max_polls is not None and self.max_polls < 1:
            raise WatchError("max_polls must be >= 1 if set")


def _digest(path: str) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
    except OSError as exc:
        raise WatchError(f"Cannot read {path}: {exc}") from exc
    return h.hexdigest()


@dataclass
class WatchState:
    digest_a: str = ""
    digest_b: str = ""
    polls: int = 0
    changes_detected: int = 0


def watch_diff(
    file_a: str,
    file_b: str,
    compute: Callable[[str, str], DiffResult],
    on_change: Callable[[DiffResult], None],
    opts: Optional[WatchOptions] = None,
) -> WatchState:
    if opts is None:
        opts = WatchOptions()

    state = WatchState()
    state.digest_a = _digest(file_a)
    state.digest_b = _digest(file_b)
    result = compute(file_a, file_b)
    on_change(result)
    state.polls = 1

    while opts.max_polls is None or state.polls < opts.max_polls:
        time.sleep(opts.interval)
        da = _digest(file_a)
        db = _digest(file_b)
        state.polls += 1
        if da != state.digest_a or db != state.digest_b:
            state.digest_a = da
            state.digest_b = db
            state.changes_detected += 1
            result = compute(file_a, file_b)
            on_change(result)

    return state
