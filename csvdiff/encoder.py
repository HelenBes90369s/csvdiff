"""Encode a DiffResult into alternative serialisation formats."""
from __future__ import annotations

import base64
import json
import zlib
from dataclasses import dataclass
from typing import Literal

from csvdiff.differ import DiffResult, RowChange, FieldChange


Encoding = Literal["json", "base64", "zlib+base64"]


class EncodeError(Exception):
    """Raised when encoding fails."""


@dataclass(frozen=True)
class EncodedDiff:
    encoding: Encoding
    data: str

    def decode(self) -> DiffResult:
        return decode_diff(self)


def _result_to_dict(result: DiffResult) -> dict:
    def fc_to_dict(fc: FieldChange) -> dict:
        return {"field": fc.field, "old": fc.old_value, "new": fc.new_value}

    def rc_to_dict(rc: RowChange) -> dict:
        return {
            "key": list(rc.key),
            "kind": rc.kind,
            "old_row": rc.old_row,
            "new_row": rc.new_row,
            "changes": [fc_to_dict(f) for f in rc.changes],
        }

    return {
        "added": [rc_to_dict(r) for r in result.added],
        "removed": [rc_to_dict(r) for r in result.removed],
        "changed": [rc_to_dict(r) for r in result.changed],
    }


def _dict_to_result(d: dict) -> DiffResult:
    def to_rc(r: dict) -> RowChange:
        return RowChange(
            key=tuple(r["key"]),
            kind=r["kind"],
            old_row=r["old_row"],
            new_row=r["new_row"],
            changes=[FieldChange(f["field"], f["old"], f["new"]) for f in r["changes"]],
        )

    return DiffResult(
        added=[to_rc(r) for r in d["added"]],
        removed=[to_rc(r) for r in d["removed"]],
        changed=[to_rc(r) for r in d["changed"]],
    )


def encode_diff(result: DiffResult, encoding: Encoding = "json") -> EncodedDiff:
    if result is None:
        raise EncodeError("result must not be None")
    raw = json.dumps(_result_to_dict(result), separators=(",", ":"))
    if encoding == "json":
        return EncodedDiff(encoding=encoding, data=raw)
    if encoding == "base64":
        return EncodedDiff(encoding=encoding, data=base64.b64encode(raw.encode()).decode())
    if encoding == "zlib+base64":
        compressed = zlib.compress(raw.encode())
        return EncodedDiff(encoding=encoding, data=base64.b64encode(compressed).decode())
    raise EncodeError(f"Unknown encoding: {encoding!r}")


def decode_diff(encoded: EncodedDiff) -> DiffResult:
    if encoded.encoding == "json":
        raw = encoded.data
    elif encoded.encoding == "base64":
        raw = base64.b64decode(encoded.data).decode()
    elif encoded.encoding == "zlib+base64":
        raw = zlib.decompress(base64.b64decode(encoded.data)).decode()
    else:
        raise EncodeError(f"Unknown encoding: {encoded.encoding!r}")
    return _dict_to_result(json.loads(raw))
