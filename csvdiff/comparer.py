"""Row-level similarity comparison between two DiffResults."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


class CompareError(Exception):
    """Raised when comparison cannot be performed."""


@dataclass(frozen=True)
class FieldOverlap:
    """Describes how two DiffResults agree or disagree on a single field."""
    field: str
    agree: int   # rows where both results have the same change (or no change)
    disagree: int  # rows where the results differ

    @property
    def agreement_rate(self) -> float:
        total = self.agree + self.disagree
        return self.agree / total if total else 1.0


@dataclass(frozen=True)
class CompareResult:
    """Summary of the comparison between two DiffResults."""
    common_keys: int
    only_in_left: int
    only_in_right: int
    field_overlaps: List[FieldOverlap]

    @property
    def overall_agreement(self) -> float:
        if not self.field_overlaps:
            return 1.0
        return sum(f.agreement_rate for f in self.field_overlaps) / len(self.field_overlaps)


def _change_index(result: DiffResult) -> Dict[tuple, Optional[RowChange]]:
    """Build a mapping from row key -> RowChange (or None for add/remove)."""
    index: Dict[tuple, Optional[RowChange]] = {}
    for change in result.changes:
        key = tuple(sorted(change.key.items()))
        index[key] = change
    return index


def compare_results(left: DiffResult, right: DiffResult) -> CompareResult:
    """Compare two DiffResults and return an overlap summary."""
    if left is None or right is None:
        raise CompareError("Both DiffResult arguments must be non-None.")

    left_idx = _change_index(left)
    right_idx = _change_index(right)

    left_keys = set(left_idx)
    right_keys = set(right_idx)
    common = left_keys & right_keys

    field_agree: Dict[str, int] = {}
    field_disagree: Dict[str, int] = {}

    for key in common:
        lc = left_idx[key]
        rc = right_idx[key]
        l_fields = {fc.field: (fc.old_value, fc.new_value) for fc in (lc.field_changes if lc else [])}
        r_fields = {fc.field: (fc.old_value, fc.new_value) for fc in (rc.field_changes if rc else [])}
        all_fields = set(l_fields) | set(r_fields)
        for f in all_fields:
            if l_fields.get(f) == r_fields.get(f):
                field_agree[f] = field_agree.get(f, 0) + 1
            else:
                field_disagree[f] = field_disagree.get(f, 0) + 1

    all_fields_seen = set(field_agree) | set(field_disagree)
    overlaps = [
        FieldOverlap(
            field=f,
            agree=field_agree.get(f, 0),
            disagree=field_disagree.get(f, 0),
        )
        for f in sorted(all_fields_seen)
    ]

    return CompareResult(
        common_keys=len(common),
        only_in_left=len(left_keys - right_keys),
        only_in_right=len(right_keys - left_keys),
        field_overlaps=overlaps,
    )
