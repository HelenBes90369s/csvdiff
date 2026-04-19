"""Audit log for diff operations — records who ran what and when."""
from __future__ import annotations

import datetime
import getpass
import json
import os
import socket
from dataclasses import dataclass, field, asdict
from typing import Optional

from csvdiff.differ import DiffResult


class AuditError(Exception):
    pass


@dataclass
class AuditEntry:
    timestamp: str
    user: str
    host: str
    file_a: str
    file_b: str
    key_columns: list[str]
    added: int
    removed: int
    changed: int
    note: Optional[str] = None

    def as_dict(self) -> dict:
        return asdict(self)


def _now_iso() -> str:
    return datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"


def build_entry(
    result: DiffResult,
    file_a: str,
    file_b: str,
    key_columns: list[str],
    note: Optional[str] = None,
) -> AuditEntry:
    if result is None:
        raise AuditError("result must not be None")
    if not file_a or not file_b:
        raise AuditError("file paths must not be empty")
    if not key_columns:
        raise AuditError("key_columns must not be empty")
    try:
        user = getpass.getuser()
    except Exception:
        user = "unknown"
    try:
        host = socket.gethostname()
    except Exception:
        host = "unknown"
    return AuditEntry(
        timestamp=_now_iso(),
        user=user,
        host=host,
        file_a=file_a,
        file_b=file_b,
        key_columns=list(key_columns),
        added=len(result.added),
        removed=len(result.removed),
        changed=len(result.changed),
        note=note,
    )


def append_audit_log(entry: AuditEntry, path: str) -> None:
    if entry is None:
        raise AuditError("entry must not be None")
    if not path or not path.strip():
        raise AuditError("path must not be blank")
    line = json.dumps(entry.as_dict())
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def load_audit_log(path: str) -> list[AuditEntry]:
    if not path or not path.strip():
        raise AuditError("path must not be blank")
    entries: list[AuditEntry] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            entries.append(AuditEntry(**d))
    return entries
