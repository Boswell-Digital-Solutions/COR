# Known issues

## 2026-10-02: Third-party `node_modules` is committed under `repo-crawler/tools/svelte-provider`

- What is wrong: `git ls-files` lists 1253 files under `repo-crawler/tools/svelte-provider/node_modules/`. Vendored packages (TypeScript, Svelte) are tracked.
- Root cause: unknown. `.gitignore` has no `node_modules/` rule.
- Effect on CI: none now. The path filter on `ci.yml` treats the vendored `*.md` files as documentation. No code reads them.
- Fix: not made. Remove the files from the index and add a `node_modules/` rule, if the probe does not need them committed.
- Status: open.

## 2026-10-17: Two workers can claim the same Centipede queue item at the same time

- What is wrong: `claim_next_queue_item` (`repo-crawler/src/centipede_queue_claim.rs:7-105`) checks for a claim file and then writes one in a separate step. Line 41 calls `claim_path.exists()`. Line 61 writes the claim through `write_json`. `write_json` (lines 361-366) calls `fs::write`, which creates or truncates the file. No lock, no `create_new` open, and no rename makes the claim exclusive. Two workers that run between line 41 and line 61 both see no claim. Both write a claim. Both return a `claimed` receipt for the same item.
- Root cause: The claim step is a check-then-write on plain files. The file system does not make it atomic.
- Effect: Both workers start the same work. The last write wins the claim file. `complete_from_claim_receipt` (`repo-crawler/src/centipede_queue_complete.rs:28-49`) compares the receipt with the claim file, so the losing worker's completion fails. The duplicate work is not prevented. A reader can also see a partly written claim file, because `fs::write` is not atomic.
- Evidence: source reading only, on `origin/master` at `11fc63c`. The race was not reproduced. Found by the BugCheck capability reconciliation (`BDS-ECOSYSTEM-BUGCHECK-CAPABILITY-RECON-v0.1`, capability C16; Forge_Command PR #638) and re-verified for this entry. The callers in the repository are the single-worker smoke binaries (`repo-crawler/src/bin/centipede_queue_*_smoke.rs`). No concurrent caller was found.
- Fix: not made. Create the claim with an exclusive open (`OpenOptions::create_new`), or write a temporary file and link it into place. Treat "already exists" as "claimed by another worker". Add a test with two concurrent claimants.
- Status: open.

## 2026-10-17: The Centipede queue has its own item lifecycle outside Forge_Command

- What is wrong: `repo-crawler` runs a file-based Centipede intake queue with its own item lifecycle. The steps are enqueue (`centipede_queue_writer.rs:7`), claim (`centipede_queue_claim.rs:7`), heartbeat (`centipede_queue_heartbeat.rs:6`), reclaim (`centipede_queue_reclaim.rs:6`), complete (`centipede_queue_complete.rs:7`), and fail (`centipede_queue_fail.rs:7`). Forge_Command does not see or control these transitions.
- Root cause: The queue was built as a local handoff path for Cortex evidence. No ruling names which Centipede queue is canonical. Forge_Command has its own Centipede ledger and run state machine.
- Effect: Forge_Command owns run lifecycle under the workspace authority table. This queue is not a Forge_Command run lifecycle. It is a second work-item state machine with the Centipede name. The reconciliation records it as `AUTHORITY_GAP-05` and asks for an operator ruling (decision D03). The reconciliation advises that BugCheck run brokering does not reuse this queue.
- Evidence: source reading on `origin/master` at `11fc63c`. Forge_Command PR #638 holds the reconciliation evidence.
- Fix: not made. It waits for the operator ruling on the canonical Centipede queue.
- Status: open.
