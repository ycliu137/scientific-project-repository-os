# bootstrap.md

## When

New session, clone, overlay, or empty instance.

## Steps

1. Confirm cwd is this repo root (`os.yaml` is here).
2. Read root `SKILL.md` (system entry).
3. Read `MAP.md`.
4. `python3 tools/project_api.py init-db` if `index/objects.db` is missing.
5. On a new host: read `env/catalog.yaml`, run the matching `create_*.sh` (`skills/runtime-env.md`).
6. `python3 tools/bridge.py status` (siblings may be absent on the template itself).
7. `python3 tools/nav.py rebuild`
8. `python3 tools/check_project.py`
9. `python3 tools/plan_pointer.py`
10. `python3 tools/project_api.py context --task <intent>` — read only listed skills.
11. Then do the user task.

## Do not

Create files under `objects/` without `project_api`; invent a third git repo as a control plane; **pre-read all `skills/`**.
