        # Cortex - Compiled System Reference

        **Designation:** cx
        **Document role:** Canonical compiled technical reference for the Cortex local file-intelligence service
        **Source:** `doc/system/`
        **Build command:** `bash doc/system/BUILD.sh`
        **Document version:** 2.0 (2026-06-22) - canonical compliance migration
        **Protocol:** BDS Documentation Protocol v2.0; BDS Repo Documentation System Canonical Compliance Standard

        > **Generated artifact warning:** `doc/cxSYSTEM.md` is assembled output. Edit
        > the source modules under `doc/system/` and rebuild. Hand edits to the
        > compiled artifact are overwritten by the next build.

        Assembly contract:

        - Command: `bash doc/system/BUILD.sh`
        - Validation: `bash doc/system/validate_snapshots.sh` runs during assembly
        - Primary output: `doc/cxSYSTEM.md`

        This `doc/system/` tree is the canonical source of truth for Cortex. It uses
        explicit **truth classes**: canonical facts define repo role, authority
        boundaries, contract behavior, runtime behavior, and verification doctrine;
        snapshot facts are dated, audit-derived counts and current implementation
        inventory that may drift between audits.

        | Part | File | Contents |
        | --- | --- | --- |
        | §1 | `00_overview/01-overview-charter.md` | 1. Overview and Charter |
| §2 | `10_service-contract/03-contract-surface.md` | 3. Contract Surface |
| §3 | `20_runtime/05-runtime-baseline.md` | Runtime Baseline |
| §4 | `30_dependencies/06-dependencies.md` | Dependencies |
| §5 | `40_governance/02-boundaries-and-doctrine.md` | 2. Boundaries and Doctrine |
| §6 | `50_operations/04-validation-and-delivery.md` | 4. Validation and Delivery |
| §7 | `99_appendices/90-appendices.md` | Appendices |

        ## Quick Assembly

        ```bash
        bash doc/system/BUILD.sh
        ```
