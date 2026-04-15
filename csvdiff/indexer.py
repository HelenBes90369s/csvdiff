"""indexer.py – build positional and key-based indices over a DiffResult.

An *index* maps every unique row key (or field name) to the list of
RowChange objects that reference it, making O(1) look-ups cheap for
downstream pipeline steps.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .differ import DiffResult, RowChange


class IndexError(Exception):  # noqa: A001
    """Raised when an indexing operation cannot be completed."""


@dataclass
class DiffIndex:
    """Holds several indices over a DiffResult for fast look-up."""

    # key -> list of RowChange (key is the tuple stored in RowChange.key)
    by_key: Dict[Tuple, List[RowChange]] = field(default_factory=dict)

    # field name -> list of RowChange that touch that field
    by_field: Dict[str, List[RowChange]] = field(default_factory=dict)

    # sequential position -> RowChange (insertion order)
    by_position: Dict[int, RowChange] = field(default_factory=dict)

    def get_by_key(self, key: Tuple) -> List[RowChange]:
        """Return all changes for *key*, or an empty list."""
        return self.by_key.get(key, [])

    def get_by_field(self, field_name: str) -> List[RowChange]:
        """Return all changes that include a change to *field_name*."""
        return self.by_field.get(field_name, [])

    def get_by_position(self, pos: int) -> Optional[RowChange]:
        """Return the change at sequential position *pos*, or None."""
        return self.by_position.get(pos)

    @property
    def size(self) -> int:
        """Total number of indexed changes."""
        return len(self.by_position)


def build_index(result: Optional[DiffResult]) -> DiffIndex:
    """Build a :class:`DiffIndex` from *result*.

    Parameters
    ----------
    result:
        The diff result to index.  Must not be ``None``.

    Returns
    -------
    DiffIndex
        Populated index ready for look-ups.

    Raises
    ------
    IndexError
        If *result* is ``None``.
    """
    if result is None:
        raise IndexError("result must not be None")

    idx = DiffIndex()
    all_changes: List[RowChange] = (
        list(result.added) + list(result.removed) + list(result.changed)
    )

    for pos, change in enumerate(all_changes):
        # positional index
        idx.by_position[pos] = change

        # key index
        key = tuple(change.key) if not isinstance(change.key, tuple) else change.key
        idx.by_key.setdefault(key, []).append(change)

        # field index – only changed rows carry field-level diffs
        for fc in change.field_changes:
            idx.by_field.setdefault(fc.field, []).append(change)

    return idx
