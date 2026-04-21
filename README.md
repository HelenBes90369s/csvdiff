# csvdiff

A fast CLI tool for diffing two CSV files with configurable key columns and
output formats.

## Installation

```bash
pip install csvdiff
```

## Quick start

```bash
csvdiff old.csv new.csv --key id
csvdiff old.csv new.csv --key id,name --format json
csvdiff old.csv new.csv --key id --format csv --output diff.csv
```

## Output formats

| Flag | Description |
|------|-------------|
| `text` (default) | Human-readable coloured diff |
| `json` | Machine-readable JSON |
| `csv` | CSV with a `_change` type column |

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | No differences found |
| 1 | Differences found |
| 2 | Error (missing file, parse error, …) |

## Python API

```python
from csvdiff import read_csv, index_rows
from csvdiff.differ import compute_diff
from csvdiff.formatter import format_diff

old_rows = read_csv("old.csv")
new_rows = read_csv("new.csv")
result = compute_diff(index_rows(old_rows, ["id"]), index_rows(new_rows, ["id"]))
print(format_diff(result, fmt="text"))
```

### Replay pipeline

Chain post-processing steps over a `DiffResult` with `replay_diff`:

```python
from csvdiff.differ_replay import ReplayOptions, replay_diff
from csvdiff.filter import filter_diff_by_columns
from csvdiff.sorter import sort_diff
from functools import partial

opts = ReplayOptions(
    steps=[
        partial(filter_diff_by_columns, columns=["name", "email"]),
        partial(sort_diff, key="name"),
    ],
    label="my-pipeline",
)
replay = replay_diff(result, opts)
print(replay.final)
print(replay.all_ok)   # True if every step succeeded
```

## Modules

| Module | Purpose |
|--------|---------|
| `parser` | Read & index CSV files |
| `differ` | Core diff algorithm |
| `formatter` | Text / JSON / CSV output |
| `filter` | Column filtering |
| `sorter` | Sort diff rows |
| `merger` | Merge diffs |
| `stats` | Aggregate statistics |
| `exporter` | Export to file |
| `validator` | Rule-based validation |
| `reporter` | High-level report builder |
| `highlighter` | ANSI colour highlighting |
| `pager` | Paginate large diffs |
| `sampler` | Random / head / tail sampling |
| `annotator` | Attach metadata annotations |
| `scorer` | Row similarity scoring |
| `normalizer` | Value normalisation |
| `grouper` | Group changes by kind/field |
| `limiter` | Hard caps on change counts |
| `matcher` | Match orphaned adds/removes |
| `deduplicator` | Remove duplicate rows |
| `classifier` | Severity classification |
| `pivotter` | Field-level pivot tables |
| `ranker` | Rank rows by change count |
| `flattener` | Flatten to list of dicts |
| `splitter` | Split diff by column value |
| `partitioner` | Partition into buckets |
| `aggregator` | Numeric field aggregation |
| `transformer` | Apply column transforms |
| `redactor` | Redact sensitive columns |
| `comparer` | Compare two diffs |
| `indexer` | Random-access index |
| `differ_patch` | Patch / apply operations |
| `resolver` | Conflict resolution |
| `renamer` | Column rename mapping |
| `caster` | Type casting |
| `masker` | Value masking |
| `encoder` | JSON serialisation |
| `compressor` | gzip compression |
| `freezer` | Immutable snapshot + checksum |
| `tagger` | Rule-based tagging |
| `trimmer` | Whitespace trimming |
| `labeler` | Attach human labels |
| `snapshotter` | Save/load snapshots to disk |
| `pruner` | Predicate-based pruning |
| `scorer2` | Weighted change scoring |
| `joiner` | Join two diffs |
| `scaler` | Numeric delta scaling |
| `aligner` | Align two diffs by key |
| `windower` | Sliding-window view |
| `differ_cache` | File-based result cache |
| `differ_watch` | Poll-based file watcher |
| `differ_timeout` | Timeout wrapper |
| `differ_retry` | Retry with back-off |
| `differ_progress` | Progress tracking |
| `differ_throttle` | Call-rate throttling |
| `differ_batch` | Batch processing |
| `differ_audit` | Audit log entries |
| `differ_hook` | Before/after hooks |
| `differ_schema` | Column schema inference |
| `differ_log` | Structured logging |
| `differ_pipeline` | Linear step pipeline |
| `differ_metrics` | Metrics collection |
| `differ_event` | Event bus |
| `differ_debounce` | Debounce rapid changes |
| `differ_lock` | File-based locking |
| `differ_notify` | Notification dispatch |
| `differ_rate` | Rate limiting |
| `differ_checkpoint` | Checkpoint / resume |
| `differ_queue` | Work queue |
| `differ_pool` | Worker pool |
| `differ_dispatcher` | Route to handlers |
| `differ_circuit` | Circuit breaker |
| `differ_replay` | Replay through transform pipeline |

## Contributing

Pull requests welcome. Please add tests for any new module.

## Licence

MIT
