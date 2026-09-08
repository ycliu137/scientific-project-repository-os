# COLD_START — new model drill

> A fresh model reads only this path and can reach **any** indexed file without grepping the tree.

**System entry:** this repo’s `SKILL.md`. Identity: `os.yaml`.  
**Default work happens in the pipeline pack.** Source/data/paper are siblings.

---

## 60-second bootstrap

```bash
# 1) Constitution + map
# read: SKILL.md → MAP.md → this file

# 2) Indexes
python3 tools/project_api.py reindex
python3 tools/project_api.py inventory
python3 tools/nav.py rebuild

# 3) Compact state + task subgraph (do not pre-read all skills)
python3 tools/plan_pointer.py
python3 tools/project_api.py context --task learning
# read only skills listed in context.read_skills_now

# 4) Sanity
python3 tools/check_project.py
python3 tools/bridge.py status
```

---

## Find anything

| Need | Command |
|------|---------|
| Object ID | `python3 tools/project_api.py resolve H_000001` |
| Alias / tool / skill | `python3 tools/nav.py resolve project_api` |
| Substring | `python3 tools/nav.py search experiment` |
| This repo then siblings | `python3 tools/nav.py anywhere <query>` |
| Named sibling | `python3 tools/bridge.py resolve source <query>` |
| Runtime create scripts | `python3 tools/nav.py resolve runtime_env` |
| Run in source cwd | `python3 tools/bridge.py run source -- pytest -q` |
| Run in data cwd | `python3 tools/bridge.py run data -- python preprocess/...` |
| Live next actions | `python3 tools/nav.py resolve next_action` |
| Task subgraph | `python3 tools/project_api.py context --task experiment` |
| Literature catalog | `python3 tools/bridge.py run ref -- python3 tools/ref_catalog.py list` |
| Backend lab | `python3 tools/lab.py list` / `init` / `promote` |
| Domain census | `python3 tools/project_api.py inventory` |

**Do not** walk `objects/`, source `src/`, or data `datasets/` randomly.

---

## Drill checklist

```bash
python3 tools/nav.py resolve skill
python3 tools/nav.py resolve project_api
python3 tools/nav.py resolve consult_plan
python3 tools/nav.py resolve next_action
python3 tools/plan_pointer.py
python3 tools/project_api.py context --task bootstrap
python3 tools/project_api.py inventory
python3 tools/check_project.py
python3 tools/bridge.py status
```

Expected: resolve prints paths; `tools/check_project.py` prints `VALID` or `VALID_WITH_WARN`; inventory may be all zeros; `bridge status` may show no siblings on the **template** itself.

---

## After locating a file

1. **Object (pipeline):** YAML via `project_api`.
2. **Source package:** edit in the source sibling; keep `pytest` green **in source cwd**.
3. **Data:** register in `catalog.yaml` + `datasets/<id>/meta.yaml`.
4. **Meeting:** `skills/meeting-record.md`.
5. **TeX note:** `skills/tex-docs.md` then compile PDF.
6. **Runtime on a new host:** `skills/runtime-env.md` then the matching `env/create_*.sh`.
7. Finish writes with Change Report + integrity.

---

## Mental model

```
                    ┌── source     (publicable package)
pipeline (entry) ──┼── data       (raw / processed / preprocess)
                    └── paper      (late; writing entry)
```

```
SKILL.md ──► MAP.md ──► index
                ├─► consult-plan → NEXT_ACTION.yaml + docs/MASTER_PLAN.md
                ├─► tools/nav.py / project_api.py / plan_pointer.py
                └─► tools/bridge.py ──► sibling SKILL.md + cwd run
```
