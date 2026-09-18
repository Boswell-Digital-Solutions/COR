"""Bounded Cortex Gnat shard runner.

Runs exactly one Gnat shard through its registered worker and prints a
schema-valid GnatWorkerReceipt.v1. `run_serial_gnat_plan` (serial_runner.py)
and `run_parallel_gnat_plan` (parallel_runner.py) already do this per shard,
but only ever in-process, inside Cortex's own Python runtime -- neither one
is a real process-boundary entry point another system's process could spawn.

DECISIONS/0019 (fa-local-owns-gnat-execution-routing) names this as the
missing piece: "Bounded parallel execution requires a later FA-Local
dispatch adapter and capability negotiation." Capability negotiation exists
today (fa-local-operator's GnatDispatchValidator::negotiate). This module is
the other half's landing point: the thing that adapter spawns as a
subprocess, one shard per call, to actually run the shard and hand back a
receipt.

Bounded to the two worker types DECISIONS/0018 authorizes for this proving
slice (markdown_syntax, plain_text_syntax); every other worker type the
registry otherwise supports is refused here, not silently run.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from cortex_runtime.gnats.models import GnatShard, SourceFingerprint
from cortex_runtime.gnats.receipt import build_failure_receipt, monotonic_ms, utc_now
from cortex_runtime.gnats.registry import GnatWorkerUnavailable, worker_for_type
from cortex_runtime.gnats.schema_validation import require_schema_valid

AUTHORIZED_WORKER_TYPES = frozenset({"markdown_syntax", "plain_text_syntax"})


class BoundedShardInputError(ValueError):
    """Raised when a GnatShard cannot even be constructed from the given input."""


def shard_from_contract(payload: dict[str, Any], *, local_path: Path) -> GnatShard:
    """Builds a `GnatShard` from a `gnat-shard.schema.json`-valid payload plus
    the real local path the contract deliberately excludes (`source_path_token`
    is a one-way derived diagnostic, not a reversible path reference -- see
    `gnat_core.source_path_token` and `planner.py`'s own shard construction)."""
    require_schema_valid(payload, schema_name="gnat-shard.schema.json")

    worker_type = payload["worker_type"]
    if worker_type not in AUTHORIZED_WORKER_TYPES:
        raise BoundedShardInputError(
            "this proving slice (DECISIONS/0018) only runs "
            + " or ".join(sorted(AUTHORIZED_WORKER_TYPES))
            + f" shards, not {worker_type!r}"
        )

    fingerprint = payload["source_fingerprint"]
    return GnatShard(
        run_id=payload["run_id"],
        shard_id=payload["shard_id"],
        ordinal=payload["ordinal"],
        worker_type=worker_type,
        source_ref=payload["source_ref"],
        source_path_token=payload["source_path_token"],
        media_type=payload["media_type"],
        source_fingerprint=SourceFingerprint(
            algorithm=fingerprint["algorithm"],
            digest=fingerprint["digest"],
            byte_count=fingerprint["byte_count"],
            modified_at=fingerprint["modified_at"],
        ),
        deadline_ms=payload["limits"]["deadline_ms"],
        max_bytes=payload["limits"]["max_bytes"],
        local_path=local_path,
    )


def run_shard(shard: GnatShard) -> dict[str, Any]:
    """Runs one shard through its registered worker, the same per-shard
    behavior `run_serial_gnat_plan` uses internally, as its own bounded unit
    independent of any multi-shard plan or reconciliation summary."""
    try:
        worker = worker_for_type(shard.worker_type)
    except GnatWorkerUnavailable:
        started_at = utc_now()
        start_ms = monotonic_ms()
        completed_at = utc_now()
        return build_failure_receipt(
            shard,
            reason_code="worker_unavailable",
            operator_visible_summary="No Cortex Gnat worker is registered for this shard.",
            source_fingerprint_before=shard.source_fingerprint,
            source_fingerprint_after=shard.source_fingerprint,
            state="failed",
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=max(0, monotonic_ms() - start_ms),
        )
    return worker.run(shard)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run exactly one Gnat shard through its registered worker and print a "
            "GnatWorkerReceipt.v1. Bounded to markdown_syntax and plain_text_syntax "
            "(DECISIONS/0018); every other worker type is refused."
        )
    )
    parser.add_argument(
        "shard",
        help="Path to a GnatShard.v1 JSON file, or '-' to read JSON from stdin.",
    )
    parser.add_argument(
        "--local-path",
        required=True,
        type=Path,
        help=(
            "Real local path of the shard's source file. Never part of the GnatShard "
            "contract itself (schemas/gnat-shard.schema.json has no such field, by "
            "design), so it must be supplied separately."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.shard == "-":
            payload = json.loads(sys.stdin.read())
        else:
            payload = json.loads(Path(args.shard).read_text(encoding="utf-8"))
        shard = shard_from_contract(payload, local_path=args.local_path)
    except (OSError, json.JSONDecodeError, BoundedShardInputError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    receipt = run_shard(shard)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["state"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
