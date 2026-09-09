# pipeline-entry.md — Default working repo

Use when `os.pack` is `pipeline`, which is the **default agent entry**.

## Do from here

- Create/modify/test/run the **source** package (`pip install -e ../<source>`; `tools/bridge.py run source -- pytest -q`).
- Fetch, register, and preprocess **data** (`skills/data-management.md`).
- Ingest and study **reference papers** in the ref sibling (`skills/reference-papers.md`).
- Objects, experiments, `docs/`, `tex_docs/`, meetings.
- **Disposable probes** in `backend_lab/` (`skills/backend-lab.md`) — short-term repro only; **never import** lab code from elsewhere; promote process/params/important results to `tex_docs/` (not lab `notes.md`).
- **Beamer talks** into an external `--out` directory (`skills/slides.md`; journal club → `skills/journal-club-slides.md`) — no permanent `slides/` tree here.
- Smoke tests in this repo’s `tests/` plus source tests in the source cwd.
- **Pipeline modules:** one directory per task under `pipelines/<module>/` with a README (`skills/pipeline-modules.md`).

## Do not

- Copy package code into `pipelines/` except thin wrappers that `import` the package.
- Add `pipelines/<module>/` without `README.md` (Purpose / Inputs / Outputs / Relations / How to run).
- Put raw datasets in this repo.
- Dump reference PDFs into this repo (they belong in `*_ref`).
- Commit `meeting_record/*` (except README) or `backend_lab/**/outputs/`.
- `import` anything under `backend_lab/` from pipelines, source, tests, or run-artefact trees.
- Treat lab `notes.md` / `outputs/` as the durable project record.
- Create a permanent tracked `slides/` package for cosmetics (use external `--out`).
- Promote throwaway lab scripts into `pipelines/` without a rewrite.
- Import pipeline from the source package.

## Source test loop

Use `os.yaml` → `runtime` (`skills/code-change.md`). Create that env with `env/create_*.sh` (`skills/runtime-env.md`). Do not call a bare `pytest` from `~/.local`.

```bash
# activate runtime.env_name if set (micromamba/conda/venv)
python -m pytest tests/ -q
# smoke/ when scripts exist under tests/smoke/
python -m pytest tests/test_smoke.py -q
python3 tools/bridge.py run source -- python -m pytest -q
python3 tools/bridge.py run ref -- python3 tools/ref_catalog.py list
python3 tools/lab.py list
python3 tools/slides.py templates
```
