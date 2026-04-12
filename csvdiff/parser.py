"""CSV parsing utilities for csvdiff."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator


class CSVParseError(Exception):
    """Raised when a CSV file cannot be parsed."""


Row = dict[str, str]


def read_csv(filepath: str | Path, delimiter: str = ",") -> tuple[list[str], list[Row]]:
    """Read a CSV file and return (headers, rows).

    Args:
        filepath: Path to the CSV file.
        delimiter: Field delimiter character.

    Returns:
        A tuple of (headers, rows) where rows is a list of dicts.

    Raises:
        CSVParseError: If the file cannot be read or parsed.
    """
    path = Path(filepath)
    if not path.exists():
        raise CSVParseError(f"File not found: {filepath}")
    if not path.is_file():
        raise CSVParseError(f"Not a file: {filepath}")

    try:
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh, delimiter=delimiter)
            if reader.fieldnames is None:
                raise CSVParseError(f"Empty or header-less CSV: {filepath}")
            headers: list[str] = list(reader.fieldnames)
            rows: list[Row] = [dict(row) for row in reader]
    except csv.Error as exc:
        raise CSVParseError(f"CSV parse error in {filepath}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise CSVParseError(f"Encoding error in {filepath}: {exc}") from exc

    return headers, rows


def index_rows(rows: list[Row], key_columns: list[str]) -> dict[tuple[str, ...], Row]:
    """Index rows by a composite key.

    Args:
        rows: List of row dicts.
        key_columns: Column names that form the composite key.

    Returns:
        A dict mapping key tuples to rows.

    Raises:
        CSVParseError: If a key column is missing or a duplicate key is found.
    """
    index: dict[tuple[str, ...], Row] = {}
    for row in rows:
        try:
            key = tuple(row[col] for col in key_columns)
        except KeyError as exc:
            raise CSVParseError(f"Key column {exc} not found in row: {row}") from exc
        if key in index:
            raise CSVParseError(f"Duplicate key {key} in CSV data")
        index[key] = row
    return index
