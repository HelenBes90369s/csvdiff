"""Tests for csvdiff.differ_replay."""
from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_replay import (
    ReplayError,
    ReplayOptions,
    ReplayResult,
    replay_diff,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


def _identity(r: DiffResult) -> DiffResult:
    return r


def _boom(r: DiffResult) -> DiffResult:
    raise ValueError("deliberate failure")


# ---------------------------------------------------------------------------
# ReplayOptions validation
# ---------------------------------------------------------------------------

def test_options_default_valid():
    opts = ReplayOptions()
    assert opts.steps == []
    assert opts.stop_on_error is True
    assert opts.label == "replay"


def test_options_non_list_steps_raises():
    with pytest.raises(ReplayError, match="steps must be a list"):
        ReplayOptions(steps="not-a-list")  # type: ignore[arg-type]


def test_options_non_callable_step_raises():
    with pytest.raises(ReplayError, match="not callable"):
        ReplayOptions(steps=[_identity, 42])  # type: ignore[list-item]


def test_options_blank_label_raises():
    with pytest.raises(ReplayError, match="label must not be blank"):
        ReplayOptions(label="   ")


def test_options_empty_label_raises():
    with pytest.raises(ReplayError, match="label must not be blank"):
        ReplayOptions(label="")


# ---------------------------------------------------------------------------
# replay_diff guard-rails
# ---------------------------------------------------------------------------

def test_replay_none_result_raises():
    opts = ReplayOptions()
    with pytest.raises(ReplayError, match="result must not be None"):
        replay_diff(None, opts)  # type: ignore[arg-type]


def test_replay_none_opts_raises():
    with pytest.raises(ReplayError, match="opts must not be None"):
        replay_diff(_empty_result(), None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# replay_diff behaviour
# ---------------------------------------------------------------------------

def test_replay_no_steps_returns_original():
    r = _empty_result()
    opts = ReplayOptions(steps=[])
    out = replay_diff(r, opts)
    assert out.final is r
    assert out.records == []
    assert out.all_ok is True
    assert out.aborted is False


def test_replay_single_identity_step():
    r = _empty_result()
    opts = ReplayOptions(steps=[_identity])
    out = replay_diff(r, opts)
    assert out.final is r
    assert len(out.records) == 1
    assert out.records[0].ok is True
    assert out.records[0].step_name == "_identity"


def test_replay_step_transforms_result():
    added_row = {"id": "1", "name": "Alice"}

    def add_one(res: DiffResult) -> DiffResult:
        return DiffResult(added=res.added + [added_row], removed=res.removed, changed=res.changed)

    r = _empty_result()
    opts = ReplayOptions(steps=[add_one])
    out = replay_diff(r, opts)
    assert len(out.final.added) == 1
    assert out.all_ok is True


def test_replay_stop_on_error_aborts():
    r = _empty_result()
    opts = ReplayOptions(steps=[_boom, _identity], stop_on_error=True)
    out = replay_diff(r, opts)
    assert out.aborted is True
    assert len(out.records) == 1
    assert out.records[0].ok is False
    assert "deliberate failure" in (out.records[0].error or "")


def test_replay_continue_on_error():
    r = _empty_result()
    opts = ReplayOptions(steps=[_boom, _identity], stop_on_error=False)
    out = replay_diff(r, opts)
    assert out.aborted is False
    assert len(out.records) == 2
    assert out.records[0].ok is False
    assert out.records[1].ok is True
    assert out.all_ok is False


def test_replay_all_ok_true_when_no_errors():
    opts = ReplayOptions(steps=[_identity, _identity])
    out = replay_diff(_empty_result(), opts)
    assert out.all_ok is True


def test_replay_record_step_index_correct():
    opts = ReplayOptions(steps=[_identity, _boom, _identity], stop_on_error=False)
    out = replay_diff(_empty_result(), opts)
    assert [r.step_index for r in out.records] == [0, 1, 2]


def test_replay_custom_label_stored():
    opts = ReplayOptions(label="my-pipeline")
    assert opts.label == "my-pipeline"
