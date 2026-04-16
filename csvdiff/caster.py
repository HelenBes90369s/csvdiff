"""Type-casting utilities for CSV diff field values."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from csvdiff.differ import DiffResult, RowChange, FieldChange


class CastError(Exception):
    pass


@dataclass
class CastOptions:
    columns: Dict[str, str]  # column -> type name: 'int', 'float', 'bool'
    strict: bool = False

    def __post_init__(self) -> None:
        if not self.columns:
            raise CastError("columns mapping must not be empty")
        allowed = {"int", "float", "bool"}
        for col, typ in self.columns.items():
            if typ not in allowed:
                raise CastError(f"unsupported type {typ!r} for column {col!r}")


def _cast_value(value: str, typ: str, strict: bool) -> Any:
    try:
        if typ == "int":
            return int(value)
        if typ == "float":
            return float(value)
        if typ == "bool":
            if value.lower() in ("1", "true", "yes"):
                return True
            if value.lower() in ("0", "false", "no"):
                return False
            raise ValueError(f"cannot cast {value!r} to bool")
    except (ValueError, AttributeError) as exc:
        if strict:
            raise CastError(str(exc)) from exc
        return value
    return value


def _cast_row(row: Dict[str, str], options: CastOptions) -> Dict[str, Any]:
    result = dict(row)
    for col, typ in options.columns.items():
        if col in result:
            result[col] = _cast_value(result[col], typ, options.strict)
    return result


def _cast_field_changes(changes: List[FieldChange], options: CastOptions) -> List[FieldChange]:
    out = []
    for fc in changes:
        if fc.field in options.columns:
            typ = options.columns[fc.field]
            old = _cast_value(fc.old_value, typ, options.strict)
            new = _cast_value(fc.new_value, typ, options.strict)
            out.append(FieldChange(field=fc.field, old_value=old, new_value=new))
        else:
            out.append(fc)
    return out


def cast_diff(result: Optional[DiffResult], options: CastOptions) -> DiffResult:
    if result is None:
        raise CastError("result must not be None")
    cast_changes = []
    for change in result.changes:
        new_before = _cast_row(change.before, options) if change.before else change.before
        new_after = _cast_row(change.after, options) if change.after else change.after
        new_fields = _cast_field_changes(change.field_changes, options)
        cast_changes.append(RowChange(
            key=change.key,
            before=new_before,
            after=new_after,
            field_changes=new_fields,
        ))
    return DiffResult(
        added=result.added,
        removed=result.removed,
        changes=cast_changes,
    )
