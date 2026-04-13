"""Output formatters for diff results."""

import json
import csv
import io
from typing import Literal
from csvdiff.differ import DiffResult, RowChange

OutputFormat = Literal["text", "json", "csv"]


def format_diff(result: DiffResult, fmt: OutputFormat = "text") -> str:
    """Format a DiffResult into a human-readable or machine-readable string."""
    if fmt == "json":
        return _format_json(result)
    elif fmt == "csv":
        return _format_csv(result)
    else:
        return _format_text(result)


def _format_text(result: DiffResult) -> str:
    lines = []

    for key in sorted(result.added):
        row = result.added[key]
        lines.append(f"+ {dict(zip(result.added, []))}")  # placeholder reset below
        lines[-1] = f"+ {_row_str(key, row)}"

    for key in sorted(result.removed):
        row = result.removed[key]
        lines.append(f"- {_row_str(key, row)}")

    for key in sorted(result.changed):
        change: RowChange = result.changed[key]
        lines.append(f"~ {_key_str(key)}")
        for col, (old_val, new_val) in change.field_changes.items():
            lines.append(f"    {col}: {old_val!r} -> {new_val!r}")

    if not lines:
        lines.append("No differences found.")

    return "\n".join(lines)


def _format_json(result: DiffResult) -> str:
    data = {
        "added": {_key_str(k): v for k, v in result.added.items()},
        "removed": {_key_str(k): v for k, v in result.removed.items()},
        "changed": {
            _key_str(k): {
                "field_changes": {
                    col: {"old": old, "new": new}
                    for col, (old, new) in v.field_changes.items()
                }
            }
            for k, v in result.changed.items()
        },
    }
    return json.dumps(data, indent=2)


def _format_csv(result: DiffResult) -> str:
    output = io.StringIO()
    writer = None

    rows = []
    for key, row in result.added.items():
        rows.append({"_diff": "added", **row})
    for key, row in result.removed.items():
        rows.append({"_diff": "removed", **row})
    for key, change in result.changed.items():
        entry = {"_diff": "changed"}
        for col, (old_val, new_val) in change.field_changes.items():
            entry[f"{col}_old"] = old_val
            entry[f"{col}_new"] = new_val
        rows.append(entry)

    if rows:
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return output.getvalue()


def _key_str(key: tuple) -> str:
    return "|".join(str(k) for k in key)


def _row_str(key: tuple, row: dict) -> str:
    return f"[{_key_str(key)}] {row}"
