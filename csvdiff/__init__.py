"""csvdiff – public API."""
from csvdiff.differ import (
    CSVDiffError,
    DiffResult,
    FieldChange,
    RowChange,
    changed_fields,
)
from csvdiff.parser import CSVParseError, index_rows, read_csv
from csvdiff.formatter import format_diff
from csvdiff.filter import exclude_columns, filter_columns, filter_diff_by_columns
from csvdiff.sorter import sort_diff, sort_keys
from csvdiff.merger import merge_diff
from csvdiff.summary import format_summary, summarize
from csvdiff.stats import compute_stats
from csvdiff.exporter import export_diff
from csvdiff.validator import assert_valid, validate_diff
from csvdiff.reporter import build_report, format_report
from csvdiff.highlighter import highlight_diff
from csvdiff.truncator import TruncateOptions
from csvdiff.sampler import SampleOptions, sample_diff
from csvdiff.annotator import annotate_diff
from csvdiff.scorer import rank_candidates, score_rows
from csvdiff.normalizer import NormalizeOptions, normalize_row
from csvdiff.grouper import group_diff
from csvdiff.limiter import LimitOptions
from csvdiff.matcher import match_orphans
from csvdiff.deduplicator import DeduplicateOptions
from csvdiff.classifier import ClassifyOptions
from csvdiff.pivotter import pivot_diff
from csvdiff.ranker import RankOptions, rank_diff
from csvdiff.flattener import flatten_diff
from csvdiff.splitter import SplitOptions, split_diff
from csvdiff.partitioner import PartitionOptions, partition_diff
from csvdiff.aggregator import aggregate_diff
from csvdiff.transformer import TransformOptions, transform_diff
from csvdiff.redactor import RedactOptions, redact_diff
from csvdiff.comparer import compare_diffs
from csvdiff.indexer import build_index
from csvdiff.differ_patch import build_patch
from csvdiff.resolver import ResolveOptions, resolve_diff
from csvdiff.renamer import RenameOptions, rename_diff
from csvdiff.caster import CastOptions, cast_diff
from csvdiff.masker import MaskOptions, mask_diff
from csvdiff.encoder import decode_diff, encode_diff
from csvdiff.compressor import compress_diff, decompress_diff
from csvdiff.freezer import freeze_diff, verify
from csvdiff.tagger import TagOptions, tag_diff
from csvdiff.trimmer import TrimOptions, trim_diff
from csvdiff.labeler import LabelOptions, label_diff
from csvdiff.snapshotter import load_snapshot, save_snapshot, snapshot_exists
from csvdiff.pruner import PruneOptions, prune_diff
from csvdiff.scorer2 import WeightOptions, score_diff
from csvdiff.joiner import JoinOptions, join_diff
from csvdiff.scaler import scale_diff
from csvdiff.aligner import align_diff
from csvdiff.windower import WindowOptions, window_diff
from csvdiff.differ_cache import CacheOptions, cache_key
from csvdiff.differ_watch import WatchOptions
from csvdiff.differ_timeout import TimeoutOptions, run_with_timeout
from csvdiff.differ_retry import RetryOptions, run_with_retry
from csvdiff.differ_progress import ProgressOptions, ProgressState
from csvdiff.differ_throttle import ThrottleOptions, ThrottleState
from csvdiff.differ_batch import BatchOptions, run_batch
from csvdiff.differ_audit import build_entry
from csvdiff.differ_hook import HookOptions, run_hooks
from csvdiff.differ_schema import build_schema
from csvdiff.differ_log import LogOptions, log_diff
from csvdiff.differ_pipeline import PipelineOptions, run_pipeline
from csvdiff.differ_metrics import DiffMetrics, MetricsOptions
from csvdiff.differ_event import EventOptions, EventState
from csvdiff.differ_debounce import DebounceOptions, DebounceState
from csvdiff.differ_lock import LockOptions
from csvdiff.differ_notify import NotifyOptions
from csvdiff.differ_rate import RateOptions, RateState
from csvdiff.differ_checkpoint import CheckpointOptions
from csvdiff.differ_queue import QueueOptions
from csvdiff.differ_pool import PoolOptions, run_pool
from csvdiff.differ_dispatcher import DispatchOptions, dispatch
from csvdiff.differ_circuit import CircuitOptions, CircuitState
from csvdiff.differ_replay import ReplayOptions, run_replay
from csvdiff.differ_tracer import TracerOptions, TracerState
from csvdiff.differ_semaphore import SemaphoreOptions, SemaphoreState
from csvdiff.differ_buffer import BufferOptions, BufferState
from csvdiff.differ_router import RouterOptions
from csvdiff.differ_cursor import CursorOptions, CursorState
from csvdiff.differ_dedupe_run import DedupeRunOptions, DedupeRunState
from csvdiff.differ_throttle_burst import (
    BurstThrottleError,
    BurstThrottleOptions,
    BurstThrottleState,
    throttle_burst,
)

__all__ = [
    "CSVDiffError",
    "CSVParseError",
    "DiffResult",
    "FieldChange",
    "RowChange",
    "BurstThrottleError",
    "BurstThrottleOptions",
    "BurstThrottleState",
    "throttle_burst",
]
