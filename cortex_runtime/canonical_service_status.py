"""Cortex's own status truth, projected onto forge-local-systems-runtime's
canonical `service-status.schema.json` (vendored at
`schemas/forge_local_runtime/`), for Forge_Command's FC-LTA-P007
(`runtime-envelope-schema-valid`).

`emit_service_status()` (`service_status.py`) remains the single source of
truth and is untouched -- this module never recomputes state. It builds
Cortex's own richer local envelope (`schemas/service-status.schema.json`,
which additionally carries `runtime_surface_summary`/`watcher_summary`/
`gnat_summary` -- real fields COR's own doctrine and tests already depend
on). The canonical schema is a DIFFERENT, external contract
(`additionalProperties: false`, no such fields) -- this module projects the
same real truth onto it by keeping only the fields both schemas share, never
inventing or hiding a real state.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

from cortex_runtime.service_status import emit_service_status

ROOT = Path(__file__).resolve().parent.parent
CANONICAL_SCHEMA_PATH = ROOT / "schemas" / "forge_local_runtime" / "service-status.schema.json"

# Every field forge-local-systems-runtime's service-status.schema.json
# defines (verbatim from that schema's own `properties`), the maximum this
# projection may ever carry.
_CANONICAL_ALLOWED_KEYS = frozenset(
    {
        "service_id",
        "service_class",
        "state",
        "degraded_subtype",
        "denied_state",
        "readiness_summary_ref",
        "readiness_summary",
        "operator_visible_message",
        "correlation_id",
        "details_redacted",
        "last_updated_at",
    }
)


@lru_cache(maxsize=1)
def _canonical_validator() -> Draft202012Validator:
    with CANONICAL_SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    return Draft202012Validator(schema)


class CanonicalServiceStatusError(Exception):
    """Raised when the projected envelope fails the canonical schema.

    A system fault, not a user error -- COR's own envelope
    (`emit_service_status()`) is already schema-validated and fail-closed;
    this would mean the two schemas' shared-field shapes have diverged.
    """


def build_canonical_service_status_envelope() -> dict[str, Any]:
    """Project COR's own real status truth onto the canonical schema.

    Never recomputes state -- reads it from `emit_service_status()`, then
    keeps only the fields the canonical schema defines. Raises
    CanonicalServiceStatusError if the projection still fails the canonical
    schema (a real divergence, not a passthrough of untrusted data).
    """
    full = emit_service_status()
    envelope = {k: v for k, v in full.items() if k in _CANONICAL_ALLOWED_KEYS}

    errors = sorted(
        _canonical_validator().iter_errors(envelope),
        key=lambda error: (".".join(str(part) for part in error.path), error.message),
    )
    if errors:
        messages = [
            f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}" for error in errors
        ]
        raise CanonicalServiceStatusError(
            "Projected envelope does not conform to the canonical schema: " + "; ".join(messages)
        )
    return envelope
