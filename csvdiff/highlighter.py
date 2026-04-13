"""Highlight changed fields in diff output using ANSI colour codes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from csvdiff.differ import FieldChange, RowChange

_RESET = "\033[0m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"


class HighlightError(Exception):
    """Raised when highlighting cannot be applied."""


@dataclass
class HighlightedField:
    field: str
    old_value: Optional[str]
    new_value: Optional[str]
    colour: str

    def render(self, *, colour: bool = True) -> str:
        if not colour:
            if self.old_value is not None and self.new_value is not None:
                return f"{self.field}: {self.old_value!r} -> {self.new_value!r}"
            if self.new_value is not None:
                return f"{self.field}: {self.new_value!r}"
            return f"{self.field}: {self.old_value!r}"
        prefix = self.colour
        reset = _RESET
        if self.old_value is not None and self.new_value is not None:
            return (
                f"{prefix}{_BOLD}{self.field}{reset}: "
                f"{_RED}{self.old_value!r}{reset} -> "
                f"{_GREEN}{self.new_value!r}{reset}"
            )
        if self.new_value is not None:
            return f"{prefix}{_BOLD}{self.field}{reset}: {_GREEN}{self.new_value!r}{reset}"
        return f"{prefix}{_BOLD}{self.field}{reset}: {_RED}{self.old_value!r}{reset}"


def highlight_row_change(change: RowChange, *, colour: bool = True) -> List[str]:
    """Return a list of rendered strings for each changed field in *change*."""
    lines: List[str] = []
    for fc in change.field_changes:
        hf = HighlightedField(
            field=fc.field,
            old_value=fc.old_value,
            new_value=fc.new_value,
            colour=_YELLOW,
        )
        lines.append(hf.render(colour=colour))
    return lines


def highlight_diff(
    changes: List[RowChange],
    *,
    colour: bool = True,
    max_rows: Optional[int] = None,
) -> str:
    """Render all *changes* as a human-readable highlighted string."""
    if not changes:
        return "No differences found."

    subset = changes if max_rows is None else changes[:max_rows]
    parts: List[str] = []
    for change in subset:
        key_str = ", ".join(str(k) for k in change.key)
        header = f"{_BOLD}Row {key_str}{_RESET}" if colour else f"Row {key_str}"
        field_lines = highlight_row_change(change, colour=colour)
        parts.append(header + "\n" + "\n".join(f"  {l}" for l in field_lines))

    if max_rows is not None and len(changes) > max_rows:
        parts.append(f"... and {len(changes) - max_rows} more row(s)")

    return "\n".join(parts)
