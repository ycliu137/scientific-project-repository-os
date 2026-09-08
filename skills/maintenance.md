# maintenance.md

- Run `python3 tools/check_project.py` after content changes.
- Orphans (file under `objects/` without index) or bad `parent_path` → fix via API.
- Reindex: `skills/reindex.md`.
- `MAP.md` is a **contract table** — do not put per-domain scaffold/live status there. Census is `index/domain_inventory.generated.yaml`.
- Overlay repos: keep `os.strictness: warn` until new files are routinely indexed; then tighten to `error` for `include_roots` only. `legacy_roots` may stay WARN forever.
- Do not bulk-create objects to make the tree look balanced.
- Do not pre-create empty `objects/` / `pipelines/` / `workspace/scratch/` for cosmetics.
