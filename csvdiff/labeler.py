"""Attach human-readable labels to diff changes based on column value rules."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
from csvdiff.differ import DiffResult, RowChange


class LabelError(Exception):
    pass


@dataclass
class LabelRule:
    name: str
    column: str
    predicate: Callable[[str], bool]


@dataclass
class LabelOptions:
    rules: List[LabelRule]
    multi: bool = False  # if False, first matching rule wins

    def __post_init__(self) -> None:
        if not self.rules:
            raise LabelError("rules must not be empty")
        for r in self.rules:
            if not r.name.strip():
                raise LabelError("rule name must not be blank")


@dataclass
class LabeledChange:
    change: RowChange
    labels: List[str] = field(default_factory=list)


def _labels_for(change: RowChange, options: LabelOptions) -> List[str]:
    row = change.new_row or change.old_row or {}
    matched: List[str] = []
    for rule in options.rules:
        val = row.get(rule.column, "")
        try:
            hit = rule.predicate(val)
        except Exception:
            hit = False
        if hit:
            matched.append(rule.name)
            if not options.multi:
                break
    return matched


def label_diff(
    result: Optional[DiffResult], options: Optional[LabelOptions]
) -> List[LabeledChange]:
    if result is None:
        raise LabelError("result must not be None")
    if options is None:
        raise LabelError("options must not be None")
    out: List[LabeledChange] = []
    for change in result.changes:
        out.append(LabeledChange(change=change, labels=_labels_for(change, options)))
    return out
