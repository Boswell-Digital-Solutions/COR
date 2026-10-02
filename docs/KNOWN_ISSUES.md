# Known issues

## 2026-10-02: Third-party `node_modules` is committed under `repo-crawler/tools/svelte-provider`

- What is wrong: `git ls-files` lists 1253 files under `repo-crawler/tools/svelte-provider/node_modules/`. Vendored packages (TypeScript, Svelte) are tracked.
- Root cause: unknown. `.gitignore` has no `node_modules/` rule.
- Effect on CI: none now. The path filter on `ci.yml` treats the vendored `*.md` files as documentation. No code reads them.
- Fix: not made. Remove the files from the index and add a `node_modules/` rule, if the probe does not need them committed.
- Status: open.
