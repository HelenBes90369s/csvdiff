"""Export DiffResult to various file formats (JSON, CSV, text)."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Union

from csvdiff.differ import DiffResult
from csvdiff.formatter import format_diff


class ExportError(Exception):
    """Raised when an export operation fails."""


_SUPPORTED_FORMATS = {"json", "csv", "text"}


def export_diff(
    result: DiffResult,
    destination: Union[str, Path],
    fmt: str = "text",
    key_columns: list[str] | None = None,
) -> None:
    """Write *result* to *destination* in the requested *fmt*.

    Parameters
    ----------
    result:       The diff result to export.
    destination:  File path to write to.  Parent directories must exist.
    fmt:          One of ``'json'``, ``'csv'``, or ``'text'``.
    key_columns:  Key column names used when *fmt* is ``'csv'``.
    """
    if fmt not in _SUPPORTED_FORMATS:
        raise ExportError(
            f"Unsupported export format {fmt!r}. "
            f"Choose one of: {', '.join(sorted(_SUPPORTED_FORMATS))}"
        )

    path = Path(destination)
    try:
        content = _render(result, fmt, key_columns or [])
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise ExportError(f"Could not write to {path}: {exc}") from exc


def _render(result: DiffResult, fmt: str, key_columns: list[str]) -> str:
    """Return the diff rendered as a string in *fmt*."""
    if fmt == "json":
        return _render_json(result)
    if fmt == "csv":
        return _render_csv(result, key_columns)
    return format_diff(result, fmt="text")


def _render_json(result: DiffResult) -> str:
    payload = {
        "added": [dict(row) for row in result.added],
        "removed": [dict(row) for row in result.removed],
        "changed": [
            {
                "key": change.key,
                "fields": [
                    {"name": fc.field, "old": fc.old_value, "new": fc.new_value}
                    for fc in change.changes
                ],
            }
            for change in result.changed
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _render_csv(result: DiffResult, key_columns: list[str]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["change_type"] + key_columns + ["field", "old_value", "new_value"])
    for row in result.added:
        writer.writerow(["added"] + [""] * len(key_columns) + ["", "", ""])
    for row in result.removed:
        writer.writerow(["removed"] + [""] * len(key_columns) + ["", "", ""])
    for change in result.changed:
        key_vals = list(change.key) if isinstance(change.key, tuple) else [change.key]
        for fc in change.changes:
            writer.writerow(["changed"] + key_vals + [fc.field, fc.old_value, fc.new_value])
    return buf.getvalue()
