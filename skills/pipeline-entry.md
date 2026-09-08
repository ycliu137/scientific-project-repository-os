# pipeline-entry.md — Default working repo

Use when `os.pack` is `pipeline`, which is the **default agent entry**.

## Do from here

- Create/modify/test/run the **source** package (`pip install -e ../<source>`; `tools/bridge.py run source -- pytest -q`).
- Fetch, register, and preprocess **data** (`skills/data-management.md`).
- Ingest and study **reference papers** in the ref sibling (`skills/reference-papers.md`).
- Objects, experiments, `docs/`, `tex_docs/`, meetings.
- Smoke tests in this repo’s `tests/` plus source tests in the source cwd.
- **Pipeline modules:** one directory per task under `pipelines/<module>/` with a README (`skills/pipeline-modules.md`).

## Do not

- Copy package code into `pipelines/` except thin wrappers that `import` the package.
- Add `pipelines/<module>/` without `README.md` (Purpose / Inputs / Outputs / Relations / How to run).
- Put raw datasets in this repo.
- Dump reference PDFs into this repo (they belong in `*_ref`).
- Commit `meeting_record/*` (except README).
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
```
