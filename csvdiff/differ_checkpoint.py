"""Checkpoint support: save and restore intermediate DiffResult states."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from csvdiff.encoder import encode, decode
from csvdiff.differ import DiffResult


class CheckpointError(Exception):
    """Raised when a checkpoint operation fails."""


@dataclass(frozen=True)
class CheckpointOptions:
    directory: str
    prefix: str = "csvdiff_checkpoint"

    def __post_init__(self) -> None:
        if not self.directory or not self.directory.strip():
            raise CheckpointError("directory must not be blank")
        if not self.prefix or not self.prefix.strip():
            raise CheckpointError("prefix must not be blank")


@dataclass(frozen=True)
class CheckpointMeta:
    path: str
    label: str
    size_bytes: int


def _checkpoint_path(opts: CheckpointOptions, label: str) -> Path:
    safe_label = label.replace(os.sep, "_").replace("/", "_")
    filename = f"{opts.prefix}_{safe_label}.json"
    return Path(opts.directory) / filename


def save_checkpoint(
    result: DiffResult,
    opts: CheckpointOptions,
    label: str,
) -> CheckpointMeta:
    """Serialise *result* to a JSON checkpoint file and return metadata."""
    if result is None:
        raise CheckpointError("result must not be None")
    if not label or not label.strip():
        raise CheckpointError("label must not be blank")

    Path(opts.directory).mkdir(parents=True, exist_ok=True)
    dest = _checkpoint_path(opts, label)
    payload = encode(result, fmt="json")
    dest.write_text(payload, encoding="utf-8")
    return CheckpointMeta(path=str(dest), label=label, size_bytes=dest.stat().st_size)


def load_checkpoint(opts: CheckpointOptions, label: str) -> DiffResult:
    """Deserialise a checkpoint file back into a DiffResult."""
    if not label or not label.strip():
        raise CheckpointError("label must not be blank")

    src = _checkpoint_path(opts, label)
    if not src.exists():
        raise CheckpointError(f"checkpoint not found: {src}")
    payload = src.read_text(encoding="utf-8")
    return decode(payload, fmt="json")


def checkpoint_exists(opts: CheckpointOptions, label: str) -> bool:
    """Return True if a checkpoint with *label* exists on disk."""
    return _checkpoint_path(opts, label).exists()


def delete_checkpoint(opts: CheckpointOptions, label: str) -> bool:
    """Delete a checkpoint file; returns True if it existed."""
    path = _checkpoint_path(opts, label)
    if path.exists():
        path.unlink()
        return True
    return False
