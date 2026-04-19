"""Tests for csvdiff.differ_notify."""
import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.differ_notify import (
    NotifyError,
    NotifyOptions,
    NotifyPayload,
    notify_diff,
)


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old=old, new=new)


def _change(key, fields=None):
    return RowChange(key=key, field_changes=fields or [_fc("a", "1", "2")])


def make_result(added=None, removed=None, changed=None) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


# --- Options validation ---

def test_options_default_valid():
    opts = NotifyOptions()
    assert "log" in opts.channels


def test_options_unknown_channel_raises():
    with pytest.raises(NotifyError, match="Unknown channel"):
        NotifyOptions(channels=["email"])


def test_options_empty_channels_raises():
    with pytest.raises(NotifyError, match="empty"):
        NotifyOptions(channels=[])


def test_options_negative_min_changes_raises():
    with pytest.raises(NotifyError, match="min_changes"):
        NotifyOptions(min_changes=-1)


# --- notify_diff ---

def test_notify_none_result_raises():
    with pytest.raises(NotifyError):
        notify_diff(None)


def test_notify_no_changes_returns_none_when_on_changes_only():
    result = make_result()
    opts = NotifyOptions(on_changes_only=True, min_changes=1)
    assert notify_diff(result, opts) is None


def test_notify_no_changes_dispatches_when_not_on_changes_only():
    result = make_result()
    opts = NotifyOptions(on_changes_only=False, channels=["log"])
    payload = notify_diff(result, opts)
    assert payload is not None
    assert payload.total == 0


def test_notify_with_changes_returns_payload():
    result = make_result(changed=[_change(("k1",))])
    opts = NotifyOptions(channels=["log"])
    payload = notify_diff(result, opts)
    assert isinstance(payload, NotifyPayload)
    assert payload.changed == 1
    assert payload.total == 1


def test_notify_callback_channel_invoked():
    received = []
    result = make_result(added=[{"id": "1"}])
    opts = NotifyOptions(channels=["callback"], on_changes_only=False)
    notify_diff(result, opts, callback=received.append)
    assert len(received) == 1
    assert received[0].added == 1


def test_notify_callback_channel_without_callback_raises():
    result = make_result(added=[{"id": "1"}])
    opts = NotifyOptions(channels=["callback"], on_changes_only=False)
    with pytest.raises(NotifyError, match="callback"):
        notify_diff(result, opts, callback=None)


def test_notify_stdout_channel(capsys):
    result = make_result(removed=[{"id": "2"}])
    opts = NotifyOptions(channels=["stdout"], on_changes_only=False)
    notify_diff(result, opts)
    captured = capsys.readouterr()
    assert "csvdiff" in captured.out


def test_payload_message_contains_counts():
    result = make_result(
        added=[{"id": "1"}],
        removed=[{"id": "2"}],
        changed=[_change(("k3",))],
    )
    opts = NotifyOptions(channels=["log"], on_changes_only=False)
    payload = notify_diff(result, opts)
    assert "1 added" in payload.message
    assert "1 removed" in payload.message
    assert "1 changed" in payload.message
