# AGENTS.md — Scientific Project Repository OS

## Mandatory

1. On session start, **read `SKILL.md` first** (L1 constitution).
2. Then `MAP.md` (+ `COLD_START.md` on first session). Do not blind-edit.
3. Compact state + subgraph: `python3 tools/plan_pointer.py` then `python3 tools/project_api.py context --task <intent>`.
4. Find files via `nav.py` / `project_api` / `bridge.py` — do not walk the tree; **do not pre-read all `skills/`**.
5. Learning / objects / evolution: `consult-plan` when `context` lists it.
6. L3 **only if** `context` listed them.
7. Siblings: `os.yaml` → `siblings` + `tools/bridge.py`. Parent folder is not a git repo. No fifth control layer.
8. **Default entry is the pipeline repo.** Implement/test/run the source package from pipeline (`pip install -e` source). Source must stay independently runnable. Pipeline **may** import source. Source **must not** import pipeline or data.
9. Prefer `tools/project_api.py` for objects (pipeline repo).
10. After adds: `python3 tools/nav.py rebuild`.
11. Done = index + dense Change Report + `tools/check_project.py` + **`skills/code-change.md`** when code/pipelines changed (pytest + `tests/smoke/` green in `runtime` env; path contract).
12. After a paper sibling exists, **write the paper from the paper repo**; read/run others through the bridge.
13. New `meeting_record/YYYYMMDD_meeting.md` → same session `YYYYMMDD_action_items.md` (`skills/meeting-record.md`). Do not commit meeting contents.
14. New `pipelines/<module>/` must include `README.md` (Purpose / Inputs / Outputs / Relations / How to run / Path contract) and a row in `pipelines/README.md` (`skills/pipeline-modules.md`).
15. New host: run the matching `env/create_*.sh` from `env/catalog.yaml` (`skills/runtime-env.md`) before pytest. Do not invent ad-hoc `~/.local` envs.
16. Write **English** everywhere except Chinese meeting records in `tex_docs/` and private `meeting_record/` (`skills/language.md`).

## Violations

- Editing `objects/**` without `project_api` (or equivalent index registration)
- Claiming done without a Change Report (or with an empty file-list shell)
- Copying source/data/objects into a paper repo
- Putting pipeline glue, meetings, or raw data into the source package
- Nesting project git repos inside this OS template as a parent mega-repo
- Importing pipeline or data from the source package
- Adding a pipeline module directory without a structured README
- Declaring a code/pipeline task done with failing tests or artefact paths that omit run parameters
- Creating runtimes only from chat-log pip lines instead of `env/create_*.sh`
- Writing Chinese in skills, objects, code, or `docs/` (Chinese meeting notes belong in `tex_docs/` / `meeting_record/`)
