"""Tests for csvdiff.differ_lock."""
import time
import pytest
from pathlib import Path
from csvdiff.differ_lock import (
    LockError, LockOptions, LockHandle,
    acquire_lock, release_lock, is_locked,
)


@pytest.fixture()
def opts(tmp_path):
    return LockOptions(lock_dir=str(tmp_path / "locks"), timeout=1.0, poll_interval=0.01)


def test_lock_options_default_valid():
    o = LockOptions()
    assert o.timeout > 0


def test_lock_options_blank_dir_raises():
    with pytest.raises(LockError):
        LockOptions(lock_dir="   ")


def test_lock_options_zero_timeout_raises():
    with pytest.raises(LockError):
        LockOptions(timeout=0)


def test_lock_options_negative_poll_raises():
    with pytest.raises(LockError):
        LockOptions(poll_interval=-0.1)


def test_lock_options_zero_stale_raises():
    with pytest.raises(LockError):
        LockOptions(stale_after=0)


def test_acquire_and_release(opts):
    handle = acquire_lock("job1", opts)
    assert Path(handle.path).exists()
    release_lock(handle)
    assert not Path(handle.path).exists()


def test_is_locked_true_while_held(opts):
    handle = acquire_lock("job2", opts)
    assert is_locked("job2", opts)
    release_lock(handle)
    assert not is_locked("job2", opts)


def test_acquire_blank_name_raises(opts):
    with pytest.raises(LockError):
        acquire_lock("", opts)


def test_release_none_raises():
    with pytest.raises(LockError):
        release_lock(None)  # type: ignore


def test_acquire_times_out_if_lock_held(opts):
    handle = acquire_lock("job3", opts)
    fast_opts = LockOptions(
        lock_dir=opts.lock_dir, timeout=0.1, poll_interval=0.01
    )
    with pytest.raises(LockError, match="could not acquire"):
        acquire_lock("job3", fast_opts)
    release_lock(handle)


def test_stale_lock_is_cleared(opts, tmp_path):
    # Create a lock file with an old mtime
    lock_dir = Path(opts.lock_dir)
    lock_dir.mkdir(parents=True, exist_ok=True)
    stale_file = lock_dir / "stale.lock"
    stale_file.write_text("99999")
    old_time = time.time() - 60
    import os
    os.utime(stale_file, (old_time, old_time))
    handle = acquire_lock("stale", opts)
    assert Path(handle.path).exists()
    release_lock(handle)


def test_lock_handle_age():
    h = LockHandle(path="/tmp/x.lock")
    time.sleep(0.01)
    assert h.age >= 0.0
