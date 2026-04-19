"""Cooperative file-based locking for concurrent diff operations."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class LockError(Exception):
    """Raised when a lock cannot be acquired or released."""


@dataclass
class LockOptions:
    lock_dir: str = ".csvdiff_locks"
    timeout: float = 5.0
    poll_interval: float = 0.05
    stale_after: float = 30.0

    def __post_init__(self) -> None:
        if not self.lock_dir or not self.lock_dir.strip():
            raise LockError("lock_dir must not be blank")
        if self.timeout <= 0:
            raise LockError("timeout must be positive")
        if self.poll_interval <= 0:
            raise LockError("poll_interval must be positive")
        if self.stale_after <= 0:
            raise LockError("stale_after must be positive")


@dataclass
class LockHandle:
    path: str
    acquired_at: float = field(default_factory=time.monotonic)

    @property
    def age(self) -> float:
        return time.monotonic() - self.acquired_at


def _lock_path(options: LockOptions, name: str) -> Path:
    return Path(options.lock_dir) / f"{name}.lock"


def acquire_lock(name: str, options: Optional[LockOptions] = None) -> LockHandle:
    """Block until the named lock is acquired or timeout is reached."""
    if not name or not name.strip():
        raise LockError("lock name must not be blank")
    opts = options or LockOptions()
    lock_file = _lock_path(opts, name)
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + opts.timeout
    while True:
        # Remove stale lock
        if lock_file.exists():
            try:
                age = time.monotonic() - lock_file.stat().st_mtime
                if age > opts.stale_after:
                    lock_file.unlink(missing_ok=True)
            except OSError:
                pass
        try:
            fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return LockHandle(path=str(lock_file))
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise LockError(f"could not acquire lock '{name}' within {opts.timeout}s")
            time.sleep(opts.poll_interval)


def release_lock(handle: LockHandle) -> None:
    """Release a previously acquired lock."""
    if handle is None:
        raise LockError("handle must not be None")
    try:
        Path(handle.path).unlink(missing_ok=True)
    except OSError as exc:
        raise LockError(f"failed to release lock: {exc}") from exc


def is_locked(name: str, options: Optional[LockOptions] = None) -> bool:
    opts = options or LockOptions()
    return _lock_path(opts, name).exists()
