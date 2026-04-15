"""Apply field-level transformations to rows in a DiffResult."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange, FieldChange


TransformFn = Callable[[str], str]


class TransformError(Exception):
    """Raised when a transformation cannot be applied."""


@dataclass
class TransformOptions:
    """Configuration for diff transformations."""

    column_transforms: Dict[str, TransformFn] = field(default_factory=dict)
    apply_to_old: bool = True
    apply_to_new: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.column_transforms, dict):
            raise TransformError("column_transforms must be a dict")


def _apply_to_row(
    row: Dict[str, str],
    transforms: Dict[str, TransformFn],
) -> Dict[str, str]:
    result = dict(row)
    for col, fn in transforms.items():
        if col in result:
            try:
                result[col] = fn(result[col])
            except Exception as exc:  # pragma: no cover
                raise TransformError(
                    f"Transform for column '{col}' raised: {exc}"
                ) from exc
    return result


def _transform_change(
    change: RowChange, opts: TransformOptions
) -> RowChange:
    transforms = opts.column_transforms

    new_old = (
        _apply_to_row(change.old_row, transforms)
        if opts.apply_to_old and change.old_row is not None
        else change.old_row
    )
    new_new = (
        _apply_to_row(change.new_row, transforms)
        if opts.apply_to_new and change.new_row is not None
        else change.new_row
    )

    new_fields: List[FieldChange] = []
    for fc in change.field_changes:
        old_val = fc.old_value
        new_val = fc.new_value
        fn = transforms.get(fc.field)
        if fn is not None:
            if opts.apply_to_old and old_val is not None:
                old_val = fn(old_val)
            if opts.apply_to_new and new_val is not None:
                new_val = fn(new_val)
        new_fields.append(FieldChange(field=fc.field, old_value=old_val, new_value=new_val))

    return RowChange(
        key=change.key,
        old_row=new_old,
        new_row=new_new,
        field_changes=new_fields,
    )


def transform_diff(
    result: Optional[DiffResult],
    opts: Optional[TransformOptions] = None,
) -> DiffResult:
    """Return a new DiffResult with field values transformed per *opts*."""
    if result is None:
        raise TransformError("result must not be None")
    if opts is None:
        opts = TransformOptions()

    return DiffResult(
        added=result.added,
        removed=result.removed,
        changed=[_transform_change(c, opts) for c in result.changed],
    )
