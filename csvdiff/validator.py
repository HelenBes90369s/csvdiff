"""Validate DiffResult objects against configurable rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from csvdiff.differ import DiffResult


class ValidationError(Exception):
    """Raised when a DiffResult violates a validation rule."""


@dataclass
class ValidationRule:
    max_added: Optional[int] = None
    max_removed: Optional[int] = None
    max_changed: Optional[int] = None
    max_change_rate: Optional[float] = None  # 0.0 – 1.0
    forbidden_fields: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    passed: bool
    violations: List[str] = field(default_factory=list)


def validate_diff(result: DiffResult, rule: ValidationRule, total_rows: int = 0) -> ValidationResult:
    """Check *result* against *rule* and return a :class:`ValidationResult`."""
    violations: List[str] = []

    if rule.max_added is not None and len(result.added) > rule.max_added:
        violations.append(
            f"added rows {len(result.added)} exceeds limit {rule.max_added}"
        )

    if rule.max_removed is not None and len(result.removed) > rule.max_removed:
        violations.append(
            f"removed rows {len(result.removed)} exceeds limit {rule.max_removed}"
        )

    if rule.max_changed is not None and len(result.changed) > rule.max_changed:
        violations.append(
            f"changed rows {len(result.changed)} exceeds limit {rule.max_changed}"
        )

    if rule.max_change_rate is not None and total_rows > 0:
        total_changes = len(result.added) + len(result.removed) + len(result.changed)
        rate = total_changes / total_rows
        if rate > rule.max_change_rate:
            violations.append(
                f"change rate {rate:.2%} exceeds limit {rule.max_change_rate:.2%}"
            )

    if rule.forbidden_fields:
        forbidden_set = set(rule.forbidden_fields)
        for row_change in result.changed:
            touched = {fc.field for fc in row_change.changes}
            hit = touched & forbidden_set
            if hit:
                violations.append(
                    f"forbidden field(s) modified in row {row_change.key}: {sorted(hit)}"
                )

    return ValidationResult(passed=len(violations) == 0, violations=violations)


def assert_valid(result: DiffResult, rule: ValidationRule, total_rows: int = 0) -> None:
    """Like :func:`validate_diff` but raises :class:`ValidationError` on failure."""
    vr = validate_diff(result, rule, total_rows)
    if not vr.passed:
        msg = "Diff validation failed:\n" + "\n".join(f"  - {v}" for v in vr.violations)
        raise ValidationError(msg)
