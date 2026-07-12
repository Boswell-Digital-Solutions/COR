# bds · Cortex

> **System identity — bds family (Boswell Digital Solutions business system, local-systems tier).**
> The bounded local file-intelligence, extraction, retrieval-preparation, and handoff-support service; a business/backend local system in the Forge **ecosystem backend**, part of `ecosystem/local-systems`.
> **Purpose:** bounded local file-intelligence and retrieval-preparation service for Forge applications — intake, syntax-only extraction, one governed retrieval-package form, and truthful service-status.
> **Not the Forge counterpart:** the public-app support boundary is `apps/public-app-local-support/cortex` (Forge family).

Cortex is the bounded local file-intelligence, extraction, retrieval-preparation, and handoff-support service for Forge applications.

This directory starts with constitutional artifacts first:

- project charter
- doctrine
- authority boundaries
- service-domain definitions
- degradation and control-surface rules
- anti-drift ADRs
- architecture boundary references

Current status:

- Wave 1 constitutional scaffold created from `docs/planning/general/cortex_constitutional_project_plan_v_2.md`
- Wave 2 and Wave 3 contract/schema enforcement in place
- Runtime Slice 1 intake validation path implemented against `schemas/intake-request.schema.json`
- Runtime Slice 2 syntax-only extraction emission path implemented for bounded local `.md` and `.txt` sources
- Runtime Slice 3 governed retrieval-package emission path implemented from ready syntax-only extraction output
- Runtime Slice 4 service-status truth path implemented for current bounded runtime surfaces and admitted source lanes
- Runtime Slice 5 bounded local PDF source lane implemented for text-layer `.pdf` files only
- Shared source-lane framework extracted for admitted-lane registration, failure posture, provenance, and service-status reporting
- Runtime Slice 6 bounded local DOCX source lane implemented for local `.docx` files only
- Runtime Slice 7 bounded local RTF source lane implemented for local `.rtf` files only
- Runtime Slice 8 bounded local ODT source lane implemented for local `.odt` files only
- Runtime Slice 9 bounded local EPUB source lane implemented for local `.epub` files only
- Post-Slice-7 hardening pass completed for contract symmetry, ugly-case lane coverage, operator-surface consistency, and future lane-admission governance
- Post-Slice-8 governance selection executed through Slice 9; EPUB is now admitted
- Post-Slice-9 governance selection completed; Scrivener is now the next planning target on a special-track project-source path, and HTML remains deferred
- Special-track Scrivener Stage 1 authority recon runtime slice implemented; Scrivener remains unadmitted, and extraction plus broader Scrivener implementation remain blocked
- Current Scrivener Stage 2 planning-control packet has now been reviewed explicitly; Decision 0016 keeps Stage 2 implementation blocked pending materially broader evidence

Start here:

- `PROJECT_CHARTER.md`
- `LOCAL_DOCTRINE.md`
- `AUTHORITY_BOUNDARIES.md`
- `PHASE_1_PLAN.md`
- `docs/architecture/boundary-matrix.md`

Runtime Slice 1:

- validate a candidate intake payload: `python -m cortex_runtime.intake_validation tests/contracts/fixtures/valid/intake-request-file-basic.json`
- run runtime tests: `make test-runtime`

Runtime Slice 2:

- emit a syntax-only extraction result from a bounded local file: `python -m cortex_runtime.extraction_emission --source-path tests/runtime/fixtures/sample-note.md --request-id local-001 --source-ref src-local`
- apply declared media-type admission to the same direct-source path: `python -m cortex_runtime.extraction_emission --source-path tests/runtime/fixtures/sample-note.md --request-id local-001 --source-ref src-local --media-type text/markdown`

Runtime Slice 3:

- emit a retrieval package from the same bounded local file path: `python -m cortex_runtime.retrieval_package_emission --source-path tests/runtime/fixtures/sample-note.md --request-id local-001 --source-ref src-local`
- apply declared media-type admission to the same direct-source retrieval path: `python -m cortex_runtime.retrieval_package_emission --source-path tests/runtime/fixtures/sample-note.md --request-id local-001 --source-ref src-local --media-type text/markdown`

Runtime Slice 4:

- emit current bounded service-status truth: `python -m cortex_runtime.service_status`

Runtime Slice 5:

- emit a syntax-only extraction result from a bounded local text-layer PDF: `python -m cortex_runtime.extraction_emission --source-path tests/runtime/fixtures/sample-note.pdf --request-id pdf-001 --source-ref pdf-local`
- emit a retrieval package from the same bounded local PDF lane: `python -m cortex_runtime.retrieval_package_emission --source-path tests/runtime/fixtures/sample-note.pdf --request-id pdf-001 --source-ref pdf-local`

Runtime Slice 6:

- emit a syntax-only extraction result from a bounded local DOCX source: `python -m cortex_runtime.extraction_emission --source-path tests/runtime/fixtures/sample-note.docx --request-id docx-001 --source-ref docx-local`
- emit a retrieval package from the same bounded local DOCX lane: `python -m cortex_runtime.retrieval_package_emission --source-path tests/runtime/fixtures/sample-note.docx --request-id docx-001 --source-ref docx-local`

Runtime Slice 7:

- emit a syntax-only extraction result from a bounded local RTF source: `python -m cortex_runtime.extraction_emission --source-path tests/runtime/fixtures/sample-note.rtf --request-id rtf-001 --source-ref rtf-local`
- emit a retrieval package from the same bounded local RTF lane: `python -m cortex_runtime.retrieval_package_emission --source-path tests/runtime/fixtures/sample-note.rtf --request-id rtf-001 --source-ref rtf-local`

Runtime Slice 8:

- emit a syntax-only extraction result from a bounded local ODT source: `python -m cortex_runtime.extraction_emission --source-path tests/runtime/fixtures/sample-note.odt --request-id odt-001 --source-ref odt-local --media-type application/vnd.oasis.opendocument.text`
- emit a retrieval package from the same bounded local ODT lane: `python -m cortex_runtime.retrieval_package_emission --source-path tests/runtime/fixtures/sample-note.odt --request-id odt-001 --source-ref odt-local --media-type application/vnd.oasis.opendocument.text`

Runtime Slice 9:

- emit a syntax-only extraction result from a bounded local EPUB source: `python -m cortex_runtime.extraction_emission --source-path tests/runtime/fixtures/sample-note.epub --request-id epub-001 --source-ref epub-local --media-type application/epub+zip`
- emit a retrieval package from the same bounded local EPUB lane: `python -m cortex_runtime.retrieval_package_emission --source-path tests/runtime/fixtures/sample-note.epub --request-id epub-001 --source-ref epub-local --media-type application/epub+zip`

Scrivener Stage 1 Authority Recon:

- emit bounded status-only authority recon from one local `.scriv` project directory: `python -m cortex_runtime.scrivener_authority_recon --source-path fixtures/scrivener/positive/scriv-mixed-structure-sanitized-v1/scriv-mixed-structure-sanitized-v1.scriv --request-id scriv-stage1-001 --source-ref scriv-local`

Admission governance:

- audit current lane symmetry before expanding admitted surfaces: `docs/source-lanes/contract-symmetry-audit.md`
- evaluate future lanes through the reusable governance checklist: `docs/source-lanes/lane-admission-playbook.md`
- compare next-lane candidates explicitly before implementation: `docs/source-lanes/next-lane-candidate-matrix.md`
- review the historical post-Slice-8 candidate comparison: `docs/source-lanes/next-lane-candidate-matrix-v2.md`
- review the post-Slice-9 candidate comparison: `docs/source-lanes/next-lane-candidate-matrix-v3.md`
- review the admitted ODT lane contract: `docs/contracts/source-lane-odt.md`
- review the ODT admission ADR: `DECISIONS/0011-odt-lane-admission.md`
- review the admitted EPUB lane contract: `docs/contracts/source-lane-epub.md`
- review the EPUB admission ADR: `DECISIONS/0013-epub-lane-admission.md`
- review the historical EPUB planning draft: `docs/contracts/source-lane-epub-draft.md`
- review the post-Slice-8 selection ADR: `DECISIONS/0012-next-lane-selection-after-slice8.md`
- review the Scrivener special-track planning draft: `docs/contracts/source-lane-scrivener-draft.md`
- review the Scrivener three-project comparative evidence review: `docs/source-lanes/scrivener/three-project-comparative-evidence-review.md`
- review the post-Slice-9 selection ADR: `DECISIONS/0014-next-lane-selection-after-slice9.md`
- review the Stage 1-only Scrivener authorization ADR: `DECISIONS/0015-scrivener-stage1-authority-recon-authorization.md`
- review the current Stage 2 authorization-review ADR: `DECISIONS/0016-scrivener-stage2-implementation-remains-blocked.md`
