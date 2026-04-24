"""Cursor-based iteration over a DiffResult for streaming or pagination use cases."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, Optional

from csvdiff.differ import DiffResult, RowChange


class CursorError(Exception):
    """Raised when cursor options or state are invalid."""


@dataclass
class CursorOptions:
    page_size: int = 50
    start: int = 0

    def __post_init__(self) -> None:
        if self.page_size <= 0:
            raise CursorError("page_size must be a positive integer")
        if self.start < 0:
            raise CursorError("start must be a non-negative integer")


@dataclass
class CursorState:
    options: CursorOptions
    _position: int = field(init=False)
    _changes: list[RowChange] = field(init=False)

    def __post_init__(self) -> None:
        self._position = self.options.start
        self._changes = []

    def load(self, result: DiffResult) -> None:
        if result is None:
            raise CursorError("result must not be None")
        self._changes = result.added + result.removed + result.changed

    @property
    def position(self) -> int:
        return self._position

    @property
    def exhausted(self) -> bool:
        return self._position >= len(self._changes)

    def next_page(self) -> list[RowChange]:
        if self.exhausted:
            return []
        end = min(self._position + self.options.page_size, len(self._changes))
        page = self._changes[self._position:end]
        self._position = end
        return page

    def reset(self) -> None:
        self._position = self.options.start


def iter_cursor(result: DiffResult, options: Optional[CursorOptions] = None) -> Iterator[list[RowChange]]:
    """Yield successive pages of RowChange objects from *result*."""
    if result is None:
        raise CursorError("result must not be None")
    opts = options or CursorOptions()
    state = CursorState(options=opts)
    state.load(result)
    while not state.exhausted:
        yield state.next_page()
