"""Tag diff rows with arbitrary string labels based on field values."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List
from csvdiff.differ import DiffResult, RowChange


class TagError(Exception):
    pass


@dataclass
class TagOptions:
    rules: Dict[str, Callable[[RowChange], bool]]
    default: str = ""

    def __post_init__(self) -> None:
        if not self.rules:
            raise TagError("rules must not be empty")
        for name in self.rules:
            if not name or not name.strip():
                raise TagError("tag name must not be blank")


@dataclass
class TaggedChange:
    change: RowChange
    tags: List[str]


def tag_diff(result: DiffResult, options: TagOptions) -> List[TaggedChange]:
    """Apply tag rules to every change in *result* and return TaggedChange list."""
    if result is None:
        raise TagError("result must not be None")
    if options is None:
        raise TagError("options must not be None")

    tagged: List[TaggedChange] = []
    all_changes = list(result.added) + list(result.removed) + list(result.changed)
    for change in all_changes:
        applied = [name for name, rule in options.rules.items() if rule(change)]
        if not applied and options.default:
            applied = [options.default]
        tagged.append(TaggedChange(change=change, tags=applied))
    return tagged


def changes_with_tag(tagged: List[TaggedChange], tag: str) -> List[RowChange]:
    """Filter to changes that carry *tag*."""
    return [t.change for t in tagged if tag in t.tags]
