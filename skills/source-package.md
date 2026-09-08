# source-package.md

The source sibling is the **publicable installable package**. It must run without pipeline or data.

## Layout (created by apply --pack source)

- `src/<pkg>/` — package
- `tests/test_smoke.py` — import test
- `pyproject.toml`, human `README.md`
- `env/` — `create_*.sh` (one per runtime) + `catalog.yaml` so publication is reproducible

## Rules

- Implement features **in source**, usually while the session is opened on **pipeline**.
- Keep `pytest` green in the **source cwd**.
- No `import` of pipeline or data.
- No meetings, raw data, or pipeline YAML objects in this repo.
- README is for humans (install, API). Agent constitution stays in `SKILL.md` (thin).
