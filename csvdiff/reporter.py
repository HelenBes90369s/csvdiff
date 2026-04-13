"""High-level report combining stats, summary, and validation results."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Optional

from csvdiff.differ import DiffResult
from csvdiff.stats import compute_stats, DiffStats
from csvdiff.summary import summarize, DiffSummary
from csvdiff.validator import ValidationRule, ValidationResult, validate_diff


@dataclass
class DiffReport:
    summary: DiffSummary
    stats: DiffStats
    validation: Optional[ValidationResult] = None


def build_report(
    result: DiffResult,
    total_rows: int = 0,
    rule: Optional[ValidationRule] = None,
) -> DiffReport:
    """Produce a :class:`DiffReport` from a completed diff."""
    summary = summarize(result)
    stats = compute_stats(result)
    validation: Optional[ValidationResult] = None
    if rule is not None:
        validation = validate_diff(result, rule, total_rows=total_rows)
    return DiffReport(summary=summary, stats=stats, validation=validation)


def format_report(report: DiffReport, fmt: str = "text") -> str:
    """Render *report* as *fmt* (``'text'`` or ``'json'``)."""
    if fmt == "json":
        return _format_json(report)
    return _format_text(report)


# ── private helpers ───────────────────────────────────────────────────────────

def _format_text(report: DiffReport) -> str:
    lines = [
        "=== Diff Report ===",
        f"  Added   : {report.summary.added_rows}",
        f"  Removed : {report.summary.removed_rows}",
        f"  Changed : {report.summary.changed_rows}",
        f"  Total Δ : {report.stats.total_changes}",
    ]
    if report.stats.most_changed_field:
        lines.append(f"  Hot field: {report.stats.most_changed_field}")
    if report.validation is not None:
        status = "PASS" if report.validation.passed else "FAIL"
        lines.append(f"  Validation: {status}")
        for v in report.validation.violations:
            lines.append(f"    ! {v}")
    return "\n".join(lines)


def _format_json(report: DiffReport) -> str:
    data: dict = {
        "summary": asdict(report.summary),
        "stats": asdict(report.stats),
    }
    if report.validation is not None:
        data["validation"] = asdict(report.validation)
    return json.dumps(data, indent=2)
