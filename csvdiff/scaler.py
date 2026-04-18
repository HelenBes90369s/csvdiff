"""Scale (normalise to a 0-1 range) numeric field-change deltas across a DiffResult."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange, FieldChange


class ScaleError(Exception):
    pass


@dataclass(frozen=True)
class ScaledField:
    field: str
    old: str
    new: str
    raw_delta: Optional[float]   # None when non-numeric
    scaled_delta: Optional[float]  # None when non-numeric or range==0


@dataclass(frozen=True)
class ScaledChange:
    key: tuple
    kind: str  # 'added' | 'removed' | 'changed'
    fields: List[ScaledField]


def _try_delta(old: str, new: str) -> Optional[float]:
    try:
        return float(new) - float(old)
    except (ValueError, TypeError):
        return None


def _field_deltas(changes: List[RowChange]) -> Dict[str, List[float]]:
    """Collect all numeric deltas per field name."""
    acc: Dict[str, List[float]] = {}
    for rc in changes:
        for fc in rc.field_changes:
            d = _try_delta(fc.old_value, fc.new_value)
            if d is not None:
                acc.setdefault(fc.field, []).append(d)
    return acc


def scale_diff(result: DiffResult) -> List[ScaledChange]:
    """Return a list of ScaledChange objects with deltas normalised per field."""
    if result is None:
        raise ScaleError("result must not be None")

    all_changes = result.added + result.removed + result.changed
    deltas_by_field = _field_deltas(result.changed)

    ranges: Dict[str, float] = {}
    mins: Dict[str, float] = {}
    for field, vals in deltas_by_field.items():
        mins[field] = min(vals)
        ranges[field] = max(vals) - min(vals)

    out: List[ScaledChange] = []
    for rc in all_changes:
        scaled_fields: List[ScaledField] = []
        for fc in rc.field_changes:
            d = _try_delta(fc.old_value, fc.new_value)
            if d is None or ranges.get(fc.field, 0.0) == 0.0:
                scaled = None
            else:
                scaled = (d - mins[fc.field]) / ranges[fc.field]
            scaled_fields.append(
                ScaledField(
                    field=fc.field,
                    old=fc.old_value,
                    new=fc.new_value,
                    raw_delta=d,
                    scaled_delta=scaled,
                )
            )
        out.append(ScaledChange(key=rc.key, kind=rc.kind, fields=scaled_fields))
    return out
