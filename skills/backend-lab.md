# backend-lab.md — Disposable probes (repro short-term, document outside)

Use when the agent (or human) needs **background / exploratory runs** in the **pipeline** repo: probes, ablations, debugging sims, one-off checks.

## Principle (non-negotiable)

**Treat all of `backend_lab/` as disposable.** Deleting any `<lab_id>/` tomorrow must not break the project.

| Horizon | What matters | Where | Git |
|---------|--------------|-------|-----|
| **Short-term** | Runnable recipe + local outputs | `backend_lab/<lab_id>/` | code + `LAB.yaml` + scratch notes **yes**; **`outputs/` no** |
| **Long-term** | Process, parameters, **important results**, conclusion | **Outside** the lab: `tex_docs/`, pipeline `docs/`, objects | yes |

Hard rules:

1. **No inbound deps:** `pipelines/`, source package, `tests/`, `experiments/`, preprocess, and other labs must **not** `import` or call `backend_lab/` code.
2. **No outbound authority:** Lab code may `import` the **source** package and read data via normal paths; it must not become an API others depend on.
3. **No durable truth inside the lab:** Do not park important results in `backend_lab/*/notes.md` or `outputs/` as the project record. Promote to `tex_docs/` (or a Change Report / object) first.
4. **Git ≠ permanent:** Committing lab scripts only helps short-term repro / audit; the tree may still be wiped after promotion.

Contrast:

| Path | Role |
|------|------|
| `backend_lab/` | Disposable sandboxes |
| `pipelines/` | Maintained runners (README required) |
| `experiments/` | Durable run artefacts for registered `EXP_*` |
| `tests/` / `tests/smoke/` | Regression / done-gate |
| `workspace/scratch/` | Even lighter drafts |
| `tex_docs/` | Durable method / result notes |

## Layout

```
backend_lab/
  README.md                 # committed
  _TEMPLATE/
    LAB.yaml
    run.py
    notes.md                # scratch only
  <lab_id>/
    LAB.yaml                # recipe (git)
    run.py / …              # disposable code (git) — never imported elsewhere
    notes.md                # scratch working notes (git) — NOT the long-term record
    outputs/                # artefacts (**gitignored**)
```

**`lab_id` naming:** `YYYYMMDD_<short_slug>` (ASCII), e.g. `20260908_factor_ablation_C`.

## `LAB.yaml` (minimum)

| Field | Meaning |
|-------|---------|
| `id` | Same as folder name |
| `created_at` | UTC ISO-8601 |
| `status` | `active` \| `done` \| `promoted` \| `discarded` |
| `purpose` | One paragraph |
| `params` | Map of run-identifying parameters (seed, n, paths, …) |
| `commands` | Exact commands from **pipeline repo root** (or lab cwd if noted) |
| `runtime` | `env_name` / `python` aligned with `os.yaml` → `runtime` when possible |
| `inputs` | Paths / sibling refs |
| `outputs_dir` | Usually `outputs/` (gitignored) |
| `repro_notes` | How to re-run; gauges / caveats |
| `promote_to` | Target `tex_docs/...` once promoted (or null) |
| `linked_objects` | Optional `H_*` / `EXP_*` |

Output and log **paths must encode** the same identifying params (`skills/code-change.md` path contract), even inside a lab.

## Workflow

```bash
# from pipeline
python3 tools/lab.py init factor_ablation_C
python3 tools/lab.py list
python3 tools/lab.py show 20260908_factor_ablation_C
# edit backend_lab/<id>/run.py + LAB.yaml; run:
python3 tools/lab.py repro 20260908_factor_ablation_C
python3 tools/lab.py repro 20260908_factor_ablation_C --exec
# durable record OUTSIDE the lab:
python3 tools/lab.py promote 20260908_factor_ablation_C --tex tex_docs/labs/factor_ablation_C
python3 tools/lab.py status 20260908_factor_ablation_C promoted
# optional: delete backend_lab/<id>/ after promotion — project must still make sense
```

Promotion writes a TeX stub under `tex_docs/` (purpose, params, commands, results). That TeX — not `notes.md` — is the long-term record. Compile via `skills/tex-docs.md`. Optionally register `EXP_*` / `R_*` if the finding enters the scientific graph.

## Agent duties

1. Prefer `backend_lab` over polluting `pipelines/` for one-off probes.
2. Fill `LAB.yaml` before treating outputs as trustworthy.
3. Never add imports from `backend_lab` into maintained code.
4. Put important results into `tex_docs/` (or objects/docs); treat lab `notes.md` as scratch.
5. After promote, labs may be deleted; rewrite into `pipelines/` + source tests only if the probe graduates.

## Anti-patterns

- `from backend_lab… import` / path hacks into lab scripts from pipelines, source, or tests
- Committing `outputs/` or treating lab notes as canon
- Leaving the only copy of an important result inside `backend_lab/`
- Using labs as a second package or second pipeline catalog
- Skipping seeds / env / commands in `LAB.yaml`
