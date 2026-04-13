"""Build and format human-readable diff reports."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from csvdiff.annotator import AnnotatedRow, annotate_diff, group_by_annotation
from csvdiff.differ import DiffResult
from csvdiff.stats import DiffStats, compute_stats


@dataclass
class DiffReport:
    """Aggregated report produced from a DiffResult."""

    stats: DiffStats
    groups: Dict[str, List[AnnotatedRow]] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)


def build_report(
    result: DiffResult,
    *,
    group_by: str = "kind",
    notes: Optional[List[str]] = None,
) -> DiffReport:
    """Compute stats and annotate *result*, returning a :class:`DiffReport`."""
    stats = compute_stats(result)
    annotated = annotate_diff(result)
    groups = group_by_annotation(annotated, group_by)
    return DiffReport(
        stats=stats,
        groups=groups,
        notes=notes or [],
    )


def format_report(report: DiffReport, fmt: str = "text") -> str:
    """Serialise *report* to *fmt* (``'text'`` or ``'json'``)."""
    if fmt == "json":
        return _format_json(report)
    if fmt == "text":
        return _format_text(report)
    raise ValueError(f"Unknown format: {fmt!r}")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _format_text(report: DiffReport) -> str:
    lines: List[str] = []
    s = report.stats
    lines.append("=== CSV Diff Report ===")
    lines.append(f"  Added   : {s.added_rows}")
    lines.append(f"  Removed : {s.removed_rows}")
    lines.append(f"  Changed : {s.changed_rows}")
    lines.append(f"  Total   : {s.total_changes}")
    if report.notes:
        lines.append("--- Notes ---")
        for note in report.notes:
            lines.append(f"  * {note}")
    if report.groups:
        lines.append("--- Groups ---")
        for group_key, rows in sorted(report.groups.items()):
            lines.append(f"  [{group_key}] {len(rows)} row(s)")
    return "\n".join(lines)


def _format_json(report: DiffReport) -> str:
    payload: Dict[str, Any] = {
        "stats": {
            "added_rows": report.stats.added_rows,
            "removed_rows": report.stats.removed_rows,
            "changed_rows": report.stats.changed_rows,
            "total_changes": report.stats.total_changes,
        },
        "groups": {
            k: len(v) for k, v in report.groups.items()
        },
        "notes": report.notes,
    }
    return json.dumps(payload, indent=2)
