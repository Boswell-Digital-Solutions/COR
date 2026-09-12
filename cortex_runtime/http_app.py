"""Cortex's bounded HTTP surface (FC-LTA-P007).

COR has never exposed HTTP before -- it is a CLI/file-producer service by
design (see `emit_service_status()`'s own docstring history and
`health_cli.py`). This is a deliberate, narrow exception, operator-authorized
for exactly one purpose: letting Forge_Command observe Cortex's own real
readiness truth over the network instead of only via a manually-run CLI
command.

Exactly one route. Per `CONTROL_SURFACE.md`'s allowed surface classes
("readiness and degraded-state indicators") -- this is not a general Cortex
API, and nothing about intake, extraction, or gnat control is exposed here.
Adding a second route is a new decision, not an extension of this one.

Port 8006, registered in the forge root `PORT_REGISTRY.md`.
"""

from __future__ import annotations

from fastapi import FastAPI

from cortex_runtime.canonical_service_status import build_canonical_service_status_envelope

app = FastAPI(
    title="Cortex (COR) — bounded service-status surface",
    description="Exactly one route: the FC-LTA-P007 service-status envelope. See CONTROL_SURFACE.md.",
    version="0.1.0",
)


@app.get("/health/service-status")
async def health_service_status() -> dict:
    return build_canonical_service_status_envelope()
