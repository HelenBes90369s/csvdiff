"""Core diffing logic for csvdiff."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class CSVDiffError(Exception):
    """Base error for differ operations."""


@dataclass(frozen=True)
class FieldChange:
    """A single field that changed between two rows."""

    field: str
    old_value: str
    new_value: str


@dataclass
class RowChange:
    """All field-level changes for a single (keyed) row."""

    key: Any  # str or tuple[str, ...]
    old_row: dict[str, str]
    new_row: dict[str, str]
    changes: list[FieldChange] = field(default_factory=list)


@dataclass
class DiffResult:
    """Complete result of diffing two CSV files."""

    added: list[dict[str, str]] = field(default_factory=list)
    removed: list[dict[str, str]] = field(default_factory=list)
    changed: list[RowChange] = field(default_factory=list)


def changed_fields(old: dict[str, str], new: dict[str, str]) -> list[FieldChange]:
    """Return a list of :class:`FieldChange` for every field that differs."""
    all_keys = set(old) | set(new)
    return [
        FieldChange(field=k, old_value=old.get(k, ""), new_value=new.get(k, ""))
        for k in sorted(all_keys)
        if old.get(k, "") != new.get(k, "")
    ]


def has_changes(result: DiffResult) -> bool:
    """Return *True* if *result* contains any differences."""
    return bool(result.added or result.removed or result.changed)


def total(result: DiffResult) -> int:
    """Return the total number of differing rows."""
    return len(result.added) + len(result.removed) + len(result.changed)


def diff(
    old_index: dict[Any, dict[str, str]],
    new_index: dict[Any, dict[str, str]],
) -> DiffResult:
    """Diff two pre-indexed CSV dicts and return a :class:`DiffResult`."""
    old_keys = set(old_index)
    new_keys = set(new_index)

    added = [new_index[k] for k in sorted(new_keys - old_keys)]
    removed = [old_index[k] for k in sorted(old_keys - new_keys)]

    changed: list[RowChange] = []
    for k in sorted(old_keys & new_keys):
        fields = changed_fields(old_index[k], new_index[k])
        if fields:
            changed.append(
                RowChange(
                    key=k,
                    old_row=old_index[k],
                    new_row=new_index[k],
                    changes=fields,
                )
            )

    return DiffResult(added=added, removed=removed, changed=changed)
