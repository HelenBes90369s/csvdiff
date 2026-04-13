"""Tests for the csvdiff CLI entry point."""

import os
import csv
import tempfile
import pytest

from csvdiff.cli import run


def write_csv(path: str, rows: list) -> None:
    if not rows:
        open(path, "w").close()
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


def test_no_differences_exits_zero(tmp_dir):
    rows = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
    a = os.path.join(tmp_dir, "a.csv")
    b = os.path.join(tmp_dir, "b.csv")
    write_csv(a, rows)
    write_csv(b, rows)
    assert run([a, b, "-k", "id"]) == 0


def test_differences_exits_one(tmp_dir):
    a_path = os.path.join(tmp_dir, "a.csv")
    b_path = os.path.join(tmp_dir, "b.csv")
    write_csv(a_path, [{"id": "1", "val": "foo"}])
    write_csv(b_path, [{"id": "1", "val": "bar"}])
    assert run([a_path, b_path, "-k", "id"]) == 1


def test_missing_file_exits_two(tmp_dir):
    a_path = os.path.join(tmp_dir, "a.csv")
    write_csv(a_path, [{"id": "1"}])
    assert run([a_path, os.path.join(tmp_dir, "missing.csv"), "-k", "id"]) == 2


def test_default_key_uses_first_column(tmp_dir):
    a_path = os.path.join(tmp_dir, "a.csv")
    b_path = os.path.join(tmp_dir, "b.csv")
    write_csv(a_path, [{"id": "1", "val": "x"}])
    write_csv(b_path, [{"id": "1", "val": "y"}])
    # No -k flag — should infer 'id' as key and detect change
    assert run([a_path, b_path]) == 1


def test_json_format_output(tmp_dir, capsys):
    a_path = os.path.join(tmp_dir, "a.csv")
    b_path = os.path.join(tmp_dir, "b.csv")
    write_csv(a_path, [{"id": "1", "val": "old"}])
    write_csv(b_path, [{"id": "1", "val": "new"}])
    run([a_path, b_path, "-k", "id", "-f", "json"])
    captured = capsys.readouterr()
    import json
    data = json.loads(captured.out)
    assert "changed" in data


def test_csv_format_output(tmp_dir, capsys):
    a_path = os.path.join(tmp_dir, "a.csv")
    b_path = os.path.join(tmp_dir, "b.csv")
    write_csv(a_path, [{"id": "1", "val": "old"}])
    write_csv(b_path, [{"id": "2", "val": "new"}])
    run([a_path, b_path, "-k", "id", "-f", "csv"])
    captured = capsys.readouterr()
    assert "status" in captured.out


def test_composite_key(tmp_dir):
    a_path = os.path.join(tmp_dir, "a.csv")
    b_path = os.path.join(tmp_dir, "b.csv")
    write_csv(a_path, [{"dept": "eng", "emp": "alice", "level": "1"}])
    write_csv(b_path, [{"dept": "eng", "emp": "alice", "level": "2"}])
    assert run([a_path, b_path, "-k", "dept", "-k", "emp"]) == 1
