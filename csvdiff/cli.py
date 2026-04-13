"""Command-line interface for csvdiff."""

import sys
import argparse
from typing import List, Optional

from csvdiff.parser import read_csv, index_rows, CSVParseError
from csvdiff.differ import diff_csv, has_changes
from csvdiff.formatter import format_diff


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csvdiff",
        description="Diff two CSV files by key column(s).",
    )
    parser.add_argument("file_a", help="Original CSV file")
    parser.add_argument("file_b", help="Modified CSV file")
    parser.add_argument(
        "-k", "--key",
        dest="keys",
        metavar="COLUMN",
        action="append",
        default=[],
        help="Key column name (repeatable for composite keys). Defaults to first column.",
    )
    parser.add_argument(
        "-f", "--format",
        dest="output_format",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding (default: utf-8).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output in text mode.",
    )
    return parser


def run(argv: Optional[List[str]] = None) -> int:
    """Entry point. Returns exit code: 0 = no diff, 1 = diff found, 2 = error."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        rows_a = read_csv(args.file_a, encoding=args.encoding)
        rows_b = read_csv(args.file_b, encoding=args.encoding)
    except CSVParseError as exc:
        print(f"csvdiff: error: {exc}", file=sys.stderr)
        return 2

    # Determine key columns
    keys = args.keys
    if not keys:
        if not rows_a and not rows_b:
            print("csvdiff: error: files are empty, cannot determine key column.", file=sys.stderr)
            return 2
        sample = rows_a[0] if rows_a else rows_b[0]
        keys = [next(iter(sample))]

    try:
        index_a = index_rows(rows_a, keys)
        index_b = index_rows(rows_b, keys)
    except (KeyError, ValueError) as exc:
        print(f"csvdiff: error: {exc}", file=sys.stderr)
        return 2

    result = diff_csv(index_a, index_b)
    output = format_diff(result, fmt=args.output_format, color=not args.no_color)
    print(output, end="" if output.endswith("\n") else "\n")

    return 1 if has_changes(result) else 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
