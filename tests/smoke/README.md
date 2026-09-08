# Smoke checks (`tests/smoke/`)

Fast start-up / wiring checks. Not a substitute for pytest under `tests/` (excluding this folder's scripts if they are not pytest files).

Run with the interpreter in `os.yaml` → `runtime` (`skills/code-change.md`).

```bash
python -m pytest tests/ -q
# optional project scripts in this folder, e.g.:
# python tests/smoke/run_all.py
```

Add scripts here as the project grows. Keep them fast and free of large data. Do **not** recreate a root `smoke/` folder.
