"""High-level diff report builder.

Combines :mod:`csvdiff.stats`, :mod:`csvdiff.summary`, and
:mod:`csvdiff.scorer` into a single human- or machine-readable report.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List

from csvdiff.differ import DiffResult
from csvdiff.stats import DiffStats, compute_stats
from csvdiff.summary import DiffSummary, summarize


@dataclass
class DiffReport:
    """Aggregated report produced from a :class:`~csvdiff.differ.DiffResult`."""

    summary: DiffSummary
    stats: DiffStats
    notes: List[str] = field(default_factory=list)


def build_report(result: DiffResult, notes: List[str] | None = None) -> DiffReport:
    """Build a :class:`DiffReport` from *result*.

    Args:
        result: The diff result to report on.
        notes:  Optional free-text annotations to embed in the report.

    Returns:
        A populated :class:`DiffReport`.
    """
    return DiffReport(
        summary=summarize(result),
        stats=compute_stats(result),
        notes=list(notes or []),
    )


def format_report(report: DiffReport, fmt: str = "text") -> str:
    """Serialise *report* to a string.

    Args:
        report: The report to format.
        fmt:    ``"text"`` (default) or ``"json"``.

    Returns:
        Formatted string representation.

    Raises:
        ValueError: When *fmt* is not recognised.
    """
    if fmt == "text":
        return _format_text(report)
    if fmt == "json":
        return _format_json(report)
    raise ValueError(f"Unknown format {fmt!r}; expected 'text' or 'json'")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _format_text(report: DiffReport) -> str:
    s = report.summary
    st = report.stats
    lines: List[str] = [
        f"Added rows   : {s.added_rows}",
        f"Removed rows : {s.removed_rows}",
        f"Changed rows : {s.changed_rows}",
        f"Total changes: {st.total_changes}",
        f"Change ratio : {st.change_ratio:.2%}",
    ]
    if st.most_changed_fields:
        top = ", ".join(st.most_changed_fields[:3])
        lines.append(f"Top fields   : {top}")
    if report.notes:
        lines.append("Notes:")
        lines.extend(f"  - {n}" for n in report.notes)
    return "\n".join(lines)


def _format_json(report: DiffReport) -> str:
    s = report.summary
    st = report.stats
    payload: Dict[str, Any] = {
        "summary": {
            "added_rows": s.added_rows,
            "removed_rows": s.removed_rows,
            "changed_rows": s.changed_rows,
        },
        "stats": {
            "total_changes": st.total_changes,
            "change_ratio": round(st.change_ratio, 6),
            "most_changed_fields": st.most_changed_fields,
        },
        "notes": report.notes,
    }
    return json.dumps(payload, indent=2)
