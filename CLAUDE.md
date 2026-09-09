# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cortex (COR) is the bounded local file-intelligence service for the Forge ecosystem: intake validation, syntax-only extraction, one governed retrieval-package emission form, and truthful service-status reporting, plus a write-once (WORM) audit trail. **Scope is bounded and frequently misread — COR does not plan, sequence, or select executors (that's FLO's job); it prepares and extracts, something else decides.** This is the business-side system at `ecosystem/local-systems/COR`; it is not `forge-cortex` (`apps/public-app-local-support/forge-cortex` is the separate public-app support variant with the same brand — the path decides which one owns the behavior).

## Common Commands

- `make validate` — validate schemas (`python scripts/validate_schemas.py`)
- `make test-runtime` — run the runtime test suite (`tests/runtime`)
- `make test-gnats` — narrow to the Gnat suites (`test_gnat_*.py`)
- `make benchmark-gnats` / `make benchmark-gnat-{pdf,docx,rtf,odt,epub}` — regenerate parallel-proof benchmarks into `docs/benchmarks/`
- `cargo test --manifest-path repo-crawler/Cargo.toml` / `cargo test --manifest-path worm/Cargo.toml` — the two Rust subprojects
- `./scripts/context-bundle.sh --list` — list context bundle presets
- `.github/workflows/ci.yml` runs `make validate && make test-runtime` plus the repo-crawler and WORM targets

## Architecture

- Contracts live in [`schemas/`](schemas/): `gnat-run-request`, `gnat-run-plan`, `gnat-dispatch-envelope`, `gnat-run-status`, `gnat-run-summary`, `gnat-cache-record`, `extraction-result`, `embedded-diagnostics` — read the schema before changing a payload.
- "Gnats" are bounded workers (`gnat_core`) — each stays inside its declared capability and must not grow into a general-purpose executor.
- Source support is lane-by-lane, not generic ingestion: admitted lanes currently include `.md`/`.txt`, text-layer `.pdf`, `.docx`, `.rtf`, `.odt`, and `.epub` (see `docs/source-lanes/` for the admission playbook and candidate matrices; `DECISIONS/` holds the ADRs). Scrivener is a special-track, read-only, unadmitted-beyond-Stage-1 source.
- The WORM audit trail (`worm/`) is write-once — append, never amend.
- `repo-crawler/` is a separate Rust subproject for repo crawling.
- Canonical reference doc is `doc/corSYSTEM.md`, assembled from `doc/system/` via `bash doc/system/BUILD.sh`.
- Governing authority is `AGENTS.md` (Cortex Constitutional Project Plan v2.1) — when this file and that authority conflict, the constitutional plan wins. Start with `PROJECT_CHARTER.md`, `LOCAL_DOCTRINE.md`, `AUTHORITY_BOUNDARIES.md` for the full doctrine.

## Notes

- Do not invent undocumented APIs, tables, routes, or environment variables.
- Do not add semantic interpretation, retrieval judgment, workflow/orchestration, or executor/agent-host behavior — see `AGENTS.md` for the full list of things Cortex may not become.
- Before claiming work complete, run the validation/test commands above and report actual results.
