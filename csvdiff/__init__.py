"""csvdiff – public API."""
from csvdiff.parser import read_csv, index_rows, CSVParseError
from csvdiff.differ import (
    DiffResult,
    RowChange,
    FieldChange,
    CSVDiffError,
    changed_fields,
)
from csvdiff.formatter import format_diff
from csvdiff.filter import filter_columns, filter_diff_by_columns, exclude_columns
from csvdiff.summary import summarize, format_summary, DiffSummary
from csvdiff.pager import paginate_diff, page_to_diff_result
from csvdiff.sorter import sort_diff, sort_keys
from csvdiff.merger import merge_diff
from csvdiff.stats import compute_stats, DiffStats
from csvdiff.exporter import export_diff
from csvdiff.validator import validate_diff, assert_valid
from csvdiff.reporter import build_report, format_report
from csvdiff.highlighter import highlight_diff
from csvdiff.truncator import truncate_diff
from csvdiff.sampler import sample_diff
from csvdiff.annotator import annotate_diff
from csvdiff.scorer import score_rows, rank_candidates
from csvdiff.normalizer import normalize_diff
from csvdiff.grouper import group_diff
from csvdiff.limiter import limit_diff
from csvdiff.matcher import match_orphans
from csvdiff.deduplicator import deduplicate_diff
from csvdiff.classifier import classify_diff
from csvdiff.pivotter import pivot_diff
from csvdiff.ranker import rank_diff
from csvdiff.flattener import flatten_diff
from csvdiff.splitter import split_diff
from csvdiff.partitioner import partition_diff
from csvdiff.aggregator import aggregate_diff
from csvdiff.transformer import transform_diff
from csvdiff.redactor import redact_diff
from csvdiff.comparer import compare_diffs
from csvdiff.indexer import build_index
from csvdiff.differ_patch import build_patch
from csvdiff.resolver import resolve_diff
from csvdiff.renamer import rename_diff
from csvdiff.caster import cast_diff
from csvdiff.masker import mask_diff
from csvdiff.encoder import encode_diff, decode_diff
from csvdiff.compressor import compress_diff, decompress_diff
from csvdiff.freezer import freeze_diff
from csvdiff.tagger import tag_diff
from csvdiff.trimmer import trim_diff
from csvdiff.labeler import label_diff
from csvdiff.snapshotter import save_snapshot, load_snapshot
from csvdiff.pruner import prune_diff
from csvdiff.scorer2 import score_diff
from csvdiff.joiner import join_diff
from csvdiff.scaler import scale_diff
from csvdiff.aligner import align_diff, aligned_keys, split_aligned

__all__ = [
    "read_csv", "index_rows", "CSVParseError",
    "DiffResult", "RowChange", "FieldChange", "CSVDiffError", "changed_fields",
    "format_diff",
    "filter_columns", "filter_diff_by_columns", "exclude_columns",
    "summarize", "format_summary", "DiffSummary",
    "paginate_diff", "page_to_diff_result",
    "sort_diff", "sort_keys",
    "merge_diff",
    "compute_stats", "DiffStats",
    "export_diff",
    "validate_diff", "assert_valid",
    "build_report", "format_report",
    "highlight_diff",
    "truncate_diff",
    "sample_diff",
    "annotate_diff",
    "score_rows", "rank_candidates",
    "normalize_diff",
    "group_diff",
    "limit_diff",
    "match_orphans",
    "deduplicate_diff",
    "classify_diff",
    "pivot_diff",
    "rank_diff",
    "flatten_diff",
    "split_diff",
    "partition_diff",
    "aggregate_diff",
    "transform_diff",
    "redact_diff",
    "compare_diffs",
    "build_index",
    "build_patch",
    "resolve_diff",
    "rename_diff",
    "cast_diff",
    "mask_diff",
    "encode_diff", "decode_diff",
    "compress_diff", "decompress_diff",
    "freeze_diff",
    "tag_diff",
    "trim_diff",
    "label_diff",
    "save_snapshot", "load_snapshot",
    "prune_diff",
    "score_diff",
    "join_diff",
    "scale_diff",
    "align_diff", "aligned_keys", "split_aligned",
]
