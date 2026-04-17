"""Encode and decode DiffResult to/from portable formats (JSON, CSV)."""
from __future__ import annotations

import csv
import io
import json
from typing import Any, Dict, List

from csvdiff.differ import DiffResult, FieldChange, RowChange


class EncodeError(Exception):
    """Raised when encoding or decoding fails."""


def fc_to_dict(fc: FieldChange) -> Dict[str, Any]:
    return {"field": fc.field, "old_value": fc.old_value, "new_value": fc.new_value}


def dict_to_fc(d: Dict[str, Any]) -> FieldChange:
    return FieldChange(field=d["field"], old_value=d["old_value"], new_value=d["new_value"])


def _result_to_dict(result: DiffResult) -> Dict[str, Any]:
    return {
        "added": result.added,
        "removed": result.removed,
        "changed": [
            {
                "key": list(c.key),
                "field_changes": [fc_to_dict(fc) for fc in c.field_changes],
            }
            for c in result.changed
        ],
    }


def _dict_to_result(d: Dict[str, Any]) -> DiffResult:
    changed = [
        RowChange(
            key=tuple(c["key"]),
            field_changes=[dict_to_fc(fc) for fc in c["field_changes"]],
        )
        for c in d.get("changed", [])
    ]
    return DiffResult(
        added=d.get("added", []),
        removed=d.get("removed", []),
        changed=changed,
    )


def encode_diff(result: DiffResult, fmt: str = "json") -> str:
    """Serialise *result* to a string in the requested *fmt* (``json`` or ``csv``)."""
    if result is None:
        raise EncodeError("result must not be None")
    if fmt == "json":
        return json.dumps(_result_to_dict(result), indent=2)
    if fmt == "csv":
        return _render_csv(result)
    raise EncodeError(f"Unknown format: {fmt!r}")


def decode(payload: str) -> DiffResult:
    """Deserialise a JSON *payload* produced by :func:`encode_diff`."""
    if not payload:
        raise EncodeError("payload must not be empty")
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise EncodeError(f"Invalid JSON: {exc}") from exc
    return _dict_to_result(data)


def _render_csv(result: DiffResult) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["kind", "key", "field", "old_value", "new_value"])
    for row in result.added:
        writer.writerow(["added", "", "", "", json.dumps(row)])
    for row in result.removed:
        writer.writerow(["removed", "", "", json.dumps(row), ""])
    for change in result.changed:
        key_str = "|".join(change.key)
        for fc in change.field_changes:
            writer.writerow(["changed", key_str, fc.field, fc.old_value, fc.new_value])
    return buf.getvalue()
