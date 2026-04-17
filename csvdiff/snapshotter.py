"""Snapshot a DiffResult to disk and restore it later."""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass
from typing import Union

from csvdiff.differ import DiffResult
from csvdiff.encoder import encode_diff, decode


class SnapshotError(Exception):
    """Raised when saving or loading a snapshot fails."""


@dataclass(frozen=True)
class SnapshotMeta:
    path: pathlib.Path
    size_bytes: int


def save_snapshot(result: DiffResult, path: Union[str, pathlib.Path]) -> SnapshotMeta:
    """Serialise *result* as JSON and write it to *path*.

    Raises SnapshotError on any I/O or encoding problem.
    """
    if result is None:
        raise SnapshotError("result must not be None")

    dest = pathlib.Path(path)
    try:
        payload = encode_diff(result, fmt="json")
        dest.write_text(payload, encoding="utf-8")
    except Exception as exc:  # pragma: no cover
        raise SnapshotError(f"Could not save snapshot to {dest}: {exc}") from exc

    return SnapshotMeta(path=dest, size_bytes=dest.stat().st_size)


def load_snapshot(path: Union[str, pathlib.Path]) -> DiffResult:
    """Read a JSON snapshot from *path* and return a DiffResult.

    Raises SnapshotError if the file is missing or malformed.
    """
    src = pathlib.Path(path)
    if not src.exists():
        raise SnapshotError(f"Snapshot file not found: {src}")

    try:
        payload = src.read_text(encoding="utf-8")
        return decode(payload)
    except SnapshotError:
        raise
    except Exception as exc:
        raise SnapshotError(f"Could not load snapshot from {src}: {exc}") from exc


def snapshot_exists(path: Union[str, pathlib.Path]) -> bool:
    """Return True if a snapshot file exists at *path*."""
    return pathlib.Path(path).exists()
