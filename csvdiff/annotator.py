"""Annotate diff rows with metadata tags (e.g. severity, category)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


class AnnotationError(Exception):
    """Raised when annotation configuration is invalid."""


@dataclass
class Annotation:
    """A single metadata tag attached to a RowChange."""

    key: str
    value: str


@dataclass
class AnnotatedRow:
    """A RowChange paired with its computed annotations."""

    change: RowChange
    annotations: List[Annotation] = field(default_factory=list)

    def get(self, key: str) -> Optional[str]:
        """Return the value for *key*, or None if not present."""
        for ann in self.annotations:
            if ann.key == key:
                return ann.value
        return None


# A rule is a callable that receives a RowChange and returns an Annotation or None.
AnnotationRule = Callable[[RowChange], Optional[Annotation]]


def _default_kind_rule(change: RowChange) -> Annotation:
    """Built-in rule: tag every row with its change kind."""
    return Annotation(key="kind", value=change.kind)


def annotate_diff(
    result: DiffResult,
    rules: Optional[List[AnnotationRule]] = None,
    *,
    include_kind: bool = True,
) -> List[AnnotatedRow]:
    """Apply *rules* to every RowChange in *result* and return annotated rows.

    Parameters
    ----------
    result:
        The diff result to annotate.
    rules:
        Extra annotation rules to apply after the built-ins.
    include_kind:
        When True (default) the built-in ``kind`` annotation is prepended.
    """
    if rules is None:
        rules = []

    active_rules: List[AnnotationRule] = []
    if include_kind:
        active_rules.append(_default_kind_rule)  # type: ignore[arg-type]
    active_rules.extend(rules)

    annotated: List[AnnotatedRow] = []
    all_changes: List[RowChange] = (
        result.added + result.removed + result.changed
    )
    for change in all_changes:
        annotations: List[Annotation] = []
        for rule in active_rules:
            ann = rule(change)
            if ann is not None:
                annotations.append(ann)
        annotated.append(AnnotatedRow(change=change, annotations=annotations))
    return annotated


def group_by_annotation(
    rows: List[AnnotatedRow], key: str
) -> Dict[str, List[AnnotatedRow]]:
    """Group *rows* by the value of annotation *key*."""
    groups: Dict[str, List[AnnotatedRow]] = {}
    for row in rows:
        value = row.get(key) or "__unset__"
        groups.setdefault(value, []).append(row)
    return groups
