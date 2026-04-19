"""Schema inference and validation for CSV diff results."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from csvdiff.differ import DiffResult


class SchemaError(Exception):
    pass


@dataclass
class ColumnSchema:
    name: str
    seen_in_added: bool = False
    seen_in_removed: bool = False
    seen_in_changed: bool = False

    def appears_in(self) -> List[str]:
        kinds = []
        if self.seen_in_added:
            kinds.append("added")
        if self.seen_in_removed:
            kinds.append("removed")
        if self.seen_in_changed:
            kinds.append("changed")
        return kinds


@dataclass
class DiffSchema:
    columns: Dict[str, ColumnSchema] = field(default_factory=dict)

    def all_columns(self) -> List[str]:
        return sorted(self.columns.keys())

    def changed_columns(self) -> List[str]:
        return sorted(k for k, v in self.columns.items() if v.seen_in_changed)


def infer_schema(result: DiffResult) -> DiffSchema:
    if result is None:
        raise SchemaError("result must not be None")
    schema = DiffSchema()

    def _ensure(col: str) -> ColumnSchema:
        if col not in schema.columns:
            schema.columns[col] = ColumnSchema(name=col)
        return schema.columns[col]

    for change in result.added:
        for col in change.row.keys():
            _ensure(col).seen_in_added = True

    for change in result.removed:
        for col in change.row.keys():
            _ensure(col).seen_in_removed = True

    for change in result.changed:
        for col in change.before.keys():
            _ensure(col)
        for fc in change.field_changes:
            _ensure(fc.field).seen_in_changed = True

    return schema


def assert_schema_subset(schema: DiffSchema, allowed: List[str]) -> None:
    """Raise SchemaError if any column in schema is not in allowed."""
    allowed_set = set(allowed)
    unknown = [c for c in schema.all_columns() if c not in allowed_set]
    if unknown:
        raise SchemaError(f"Unknown columns in diff: {unknown}")
