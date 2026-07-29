# Cortex (COR) — Claude Code Context

Local file intelligence: crawl, syntax extraction, retrieval prep, WORM audit.

> **Scope is bounded and frequently misread.** COR does **not** plan, sequence, or select
> executors — that is FLO's job. COR prepares and extracts; something else decides.

> **Not `forge-cortex`.** Same brand, two families. This is the business-side system at
> `ecosystem/local-systems/COR`; `apps/public-app-local-support/forge-cortex` is the public-app
> support variant. Path decides which one owns the behaviour.

Canonical reference: `doc/corSYSTEM.md`, assembled from `doc/system/` via `bash doc/system/BUILD.sh`.
Contracts: [`schemas/`](schemas/) — `gnat-run-request`, `gnat-run-plan`, `gnat-dispatch-envelope`,
`gnat-run-status`, `gnat-run-summary`, `gnat-cache-record`, `extraction-result`,
`embedded-diagnostics`. Read the schema before changing a payload.

---

## Boundaries

- Gnats are **bounded workers**. Keep each one inside its declared capability; do not grow one
  into a general-purpose executor.
- The WORM audit trail is write-once — append, never amend.
- Do not invent undocumented APIs, tables, routes, or environment variables.

---

## Verification

```bash
make validate && make test-runtime
```

That is what `.github/workflows/ci.yml` runs, plus the repo-crawler and WORM targets.
`make test-gnats` narrows to the Gnat suites; `make benchmark-gnats` regenerates the parallel
proof in `docs/benchmarks/`.

```bash
./scripts/context-bundle.sh --list
```
