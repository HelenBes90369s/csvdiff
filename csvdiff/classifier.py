"""Classify diff row changes by severity based on which fields changed."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional

from csvdiff.differ import DiffResult, RowChange


class ClassifyError(Exception):
    """Raised when classification configuration is invalid."""


@dataclass(frozen=True)
class ClassifyOptions:
    critical_fields: FrozenSet[str]
    warning_fields: FrozenSet[str]

    def __post_init__(self) -> None:
        overlap = self.critical_fields & self.warning_fields
        if overlap:
            raise ClassifyError(
                f"Fields appear in both critical and warning sets: {sorted(overlap)}"
            )


@dataclass(frozen=True)
class ClassifiedChange:
    change: RowChange
    severity: str  # "critical", "warning", or "info"


def _severity(change: RowChange, opts: ClassifyOptions) -> str:
    """Return the highest severity level triggered by a RowChange."""
    if change.kind in ("added", "removed"):
        return "info"
    changed_names: FrozenSet[str] = frozenset(
        fc.field for fc in (change.changes or [])
    )
    if changed_names & opts.critical_fields:
        return "critical"
    if changed_names & opts.warning_fields:
        return "warning"
    return "info"


def classify_diff(
    result: DiffResult,
    opts: ClassifyOptions,
) -> List[ClassifiedChange]:
    """Return every RowChange annotated with a severity label."""
    out: List[ClassifiedChange] = []
    for change in result.changes:
        out.append(ClassifiedChange(change=change, severity=_severity(change, opts)))
    return out


def severity_counts(classified: List[ClassifiedChange]) -> Dict[str, int]:
    """Return a mapping of severity label -> count."""
    counts: Dict[str, int] = {"critical": 0, "warning": 0, "info": 0}
    for cc in classified:
        counts[cc.severity] = counts.get(cc.severity, 0) + 1
    return counts
