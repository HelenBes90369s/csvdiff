"""Hedged execution: run two callables in parallel and return the first result.

If the primary callable does not complete within `hedge_after` seconds,
a secondary callable is launched concurrently.  Whichever finishes first
wins; the other is discarded.  This is the classic "hedged request" pattern
used to reduce tail latency.
"""
from __future__ import annotations

import concurrent.futures
from dataclasses import dataclass, field
from typing import Callable, Any

from csvdiff.differ import DiffResult


class HedgeError(Exception):
    """Raised for invalid hedge configuration or execution failure."""


@dataclass
class HedgeOptions:
    hedge_after: float = 0.5   # seconds before launching secondary callable
    timeout: float = 30.0      # total wall-clock budget in seconds
    label: str = "hedge"

    def __post_init__(self) -> None:
        if self.hedge_after <= 0:
            raise HedgeError("hedge_after must be positive")
        if self.timeout <= 0:
            raise HedgeError("timeout must be positive")
        if self.hedge_after >= self.timeout:
            raise HedgeError("hedge_after must be less than timeout")
        if not self.label or not self.label.strip():
            raise HedgeError("label must not be blank")


@dataclass
class HedgeResult:
    result: DiffResult
    used_hedge: bool          # True when the secondary callable won
    winner: str               # 'primary' or 'secondary'
    elapsed: float            # wall-clock seconds until result was available
    label: str = ""

    @property
    def ok(self) -> bool:
        return self.result is not None


def run_hedged(
    primary: Callable[[], DiffResult],
    secondary: Callable[[], DiffResult],
    options: HedgeOptions | None = None,
) -> HedgeResult:
    """Execute *primary*; if it stalls, also fire *secondary*.

    Returns a :class:`HedgeResult` for whichever callable finishes first.
    Raises :class:`HedgeError` on timeout or if both callables raise.
    """
    if primary is None or secondary is None:
        raise HedgeError("primary and secondary callables must not be None")
    opts = options or HedgeOptions()

    import time
    t0 = time.monotonic()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        fut_primary: concurrent.futures.Future[DiffResult] = pool.submit(primary)

        # Wait for primary up to hedge_after seconds
        done, _ = concurrent.futures.wait(
            [fut_primary], timeout=opts.hedge_after
        )

        if done:
            # Primary finished within hedge window — no need to hedge
            result = fut_primary.result()
            elapsed = time.monotonic() - t0
            return HedgeResult(
                result=result,
                used_hedge=False,
                winner="primary",
                elapsed=elapsed,
                label=opts.label,
            )

        # Primary is slow — launch secondary
        fut_secondary: concurrent.futures.Future[DiffResult] = pool.submit(secondary)
        remaining = opts.timeout - (time.monotonic() - t0)
        if remaining <= 0:
            raise HedgeError(f"[{opts.label}] timeout before secondary could start")

        done2, _ = concurrent.futures.wait(
            [fut_primary, fut_secondary],
            timeout=remaining,
            return_when=concurrent.futures.FIRST_COMPLETED,
        )

        if not done2:
            raise HedgeError(f"[{opts.label}] both callables exceeded timeout")

        winner_fut = next(iter(done2))
        used_hedge = winner_fut is fut_secondary
        winner_label = "secondary" if used_hedge else "primary"
        result = winner_fut.result()  # re-raises if the callable itself raised
        elapsed = time.monotonic() - t0
        return HedgeResult(
            result=result,
            used_hedge=used_hedge,
            winner=winner_label,
            elapsed=elapsed,
            label=opts.label,
        )
