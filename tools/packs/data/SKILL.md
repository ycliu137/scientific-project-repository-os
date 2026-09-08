# SKILL.md — Data pack

> Thin constitution. **Operate from the pipeline sibling** (`tools/bridge.py`).

**Pack:** data  
Layout default: `skills/data-management.md` — **adapt per project** and write the choice down.

- `catalog.yaml` — ids
- `datasets/<id>/meta.yaml` + `raw/` + `processed/`
- `integrated/<combo>/` — merges
- `preprocess/` — may import source; must not import pipeline

Keep **raw** immutable. Gitignore bulky `raw/` by default.

Bootstrap: this file → `MAP.md` → `catalog.yaml`. Prefer pipeline as the session root.
