"""Output formatters for diff results."""

import json
import sys
from typing import TextIO

from csvdiff.differ import DiffResult
from csvdiff.summary import DiffSummary, format_summary


def format_diff(
    result: DiffResult,
    summary: DiffSummary | None = None,
    fmt: str = "text",
    out: TextIO = sys.stdout,
) -> None:
    """Write formatted diff to *out*.

    Args:
        result: The diff result containing added, removed, and changed rows.
        summary: Optional summary statistics to include in the output.
        fmt: Output format; one of ``"text"``, ``"json"``, or ``"csv"``.
        out: File-like object to write output to (defaults to stdout).

    Raises:
        ValueError: If *fmt* is not a recognised format string.
    """
    if fmt == "text":
        _format_text(result, summary, out)
    elif fmt == "json":
        _format_json(result, summary, out)
    elif fmt == "csv":
        _format_csv(result, out)
    else:
        raise ValueError(f"Unknown format: {fmt!r}")


def _format_text(
    result: DiffResult,
    summary: DiffSummary | None,
    out: TextIO,
) -> None:
    if not result.added and not result.removed and not result.changed:
        out.write("No differences found.\n")
        if summary:
            out.write("\n" + format_summary(summary) + "\n")
        return

    for row in result.added:
        out.write(f"+ {_row_str(row)}\n")
    for row in result.removed:
        out.write(f"- {_row_str(row)}\n")
    for change in result.changed:
        key = _key_str(change.key)
        out.write(f"~ [{key}] {change.field}: {change.old_value!r} -> {change.new_value!r}\n")

    if summary:
        out.write("\n" + format_summary(summary) + "\n")


def _format_json(
    result: DiffResult,
    summary: DiffSummary | None,
    out: TextIO,
) -> None:
    payload: dict = {
        "added": result.added,
        "removed": result.removed,
        "changed": [
            {
                "key": list(c.key),
                "field": c.field,
                "old": c.old_value,
                "new": c.new_value,
            }
            for c in result.changed
        ],
    }
    if summary:
        payload["summary"] = {
            "rows_left": summary.total_rows_left,
            "rows_right": summary.total_rows_right,
            "added": summary.added,
            "removed": summary.removed,
            "changed": summary.changed,
            "unchanged": summary.unchanged,
            "change_rate": round(summary.change_rate, 4),
        }
    json.dump(payload, out, indent=2)
    out.write("\n")


def _format_csv(result: DiffResult, out: TextIO) -> None:
    out.write("change_type,key,field,old_value,new_value\n")
    for row in result.added:
        out.write(f"added,{_row_str(row)},,,\n")
    for row in result.removed:
        out.write(f"removed,{_row_str(row)},,,\n")
    for change in result.changed:
        key = _key_str(change.key)
        out.write(f"changed,{key},{change.field},{change.old_value},{change.new_value}\n")


def _row_str(row: dict) -> str:
    return " ".join(f"{k}={v}" for k, v in row.items())


def _key_str(key: tuple) -> str:
    return "|".join(str(k) for k in key)
