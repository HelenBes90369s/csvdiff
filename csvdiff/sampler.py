"""Random sampling of rows within a DiffResult."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from csvdiff.differ import DiffResult, RowChange


class SampleError(ValueError):
    """Raised when sampling parameters are invalid."""


@dataclass
class SampleOptions:
    n: Optional[int] = None          # absolute count per bucket
    fraction: Optional[float] = None  # 0.0 – 1.0 fraction per bucket
    seed: Optional[int] = None

    def __post_init__(self) -> None:
        if self.n is not None and self.fraction is not None:
            raise SampleError("Specify either 'n' or 'fraction', not both.")
        if self.n is not None and self.n < 0:
            raise SampleError("n must be >= 0")
        if self.fraction is not None and not (0.0 <= self.fraction <= 1.0):
            raise SampleError("fraction must be between 0.0 and 1.0")


def _sample(rows: list[RowChange], opts: SampleOptions, rng: random.Random) -> list[RowChange]:
    if not rows:
        return []
    if opts.n is not None:
        k = min(opts.n, len(rows))
    elif opts.fraction is not None:
        k = max(0, round(len(rows) * opts.fraction))
    else:
        return list(rows)
    return rng.sample(rows, k)


def sample_diff(result: DiffResult, opts: SampleOptions) -> DiffResult:
    """Return a new DiffResult containing a random sample of each change bucket."""
    rng = random.Random(opts.seed)
    return DiffResult(
        added=_sample(result.added, opts, rng),
        removed=_sample(result.removed, opts, rng),
        changed=_sample(result.changed, opts, rng),
    )
