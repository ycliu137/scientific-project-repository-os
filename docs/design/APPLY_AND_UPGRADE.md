# APPLY_AND_UPGRADE — how the template meets instances (safe, repeatable)

Status: template design. Tool: `tools/apply_to_repo.py`.

The OS template and each scientific instance both evolve. Apply must be
**safe on first contact** and **repeatable afterward** without destroying
either side's improvements.

## Three modes

| Mode | Flags | Name collision policy |
|------|-------|------------------------|
| **Instantiate** | empty target / `--layout siblings` | Write all shipped files (new tree). |
| **First overlay** | `--target …` **without** `--upgrade` | If dest **exists → keep**. Only **add missing** kernel files. |
| **Upgrade** | `--target . --upgrade` | See hash rules below. |

```bash
python3 /path/to/scientific-project-repository-os/tools/apply_to_repo.py \
  --target . --upgrade --dry-run
```

## Upgrade hash rules (both sides keep their work)

Manifest: `workspace/current/OS_APPLIED.yaml` — sha256 of each shipped path as of
the last successful apply/upgrade.

| Instance vs last apply | Template vs last apply | Action |
|------------------------|------------------------|--------|
| unchanged | changed | **refresh** (safe copy from template) |
| unchanged | unchanged | keep |
| changed | unchanged | keep (instance-only edit) |
| changed | changed | **absorb** — do **not** overwrite; list in `OS_ABSORB.md` |
| (no manifest) identical to template | — | synced (record hash) |
| (no manifest) differs from template | — | **absorb** — do not overwrite |

**KEEP_ON_UPGRADE** always keep (ledger, comprehension, NEXT_ACTION, MASTER_PLAN,
NOTATION) regardless of hashes.

**Never overwrite an instance-modified kernel file.** The agent must merge
template improvements *into* the instance file so both updates remain.

## Absorb workflow (agent)

After `--upgrade`, if `workspace/current/OS_ABSORB.md` lists `absorb_needed`:

1. Open each instance path and the matching file in the template checkout.
2. Merge template additions/fixes into the **instance** copy; retain instance
   science and project-specific wording.
3. `python3 tools/apply_to_repo.py --target . --record-hashes`
4. Re-run `--upgrade --dry-run` until `absorb=0`.
5. `python3 tools/nav.py rebuild && python3 tools/check_project.py`

## What apply never touches

- `pipelines/`, `objects/`, `dat/`, instance labs
- Instance Change Reports (except shipped `_TEMPLATE` / schema)
- Instance-only design docs not in the template file list
- Source `src/`, data corpora, ref paper PDFs

## Both sides improved — recipe

1. Commit the instance.
2. Update the template repo.
3. `--upgrade --dry-run` → inspect `refresh` / `absorb` / `copy`.
4. `--upgrade` for real → auto-refresh clean files; write `OS_ABSORB.yaml`.
5. Agent absorbs listed files; `--record-hashes`.
6. Prefer science in ledger / experiment plans / objects so kernel forks stay rare.

## Design rule for maintainers

- Kernel skills/tools stay **generic**.
- Prefer **additive** new files so upgrades often only `copy`.
- Bump `os.version` when the apply contract changes.
- Never “fix” divergence by clobbering the instance.
