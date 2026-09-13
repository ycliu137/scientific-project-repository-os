# consult-plan.md — Plan as procedure (not homework dump)

Do **not** require a full read of every design note every session.

## Document layers

| Layer | Path | When to open |
|-------|------|----------------|
| Constitution | `SKILL.md` | Always (Bootstrap) |
| **Campaign authority** | instance plan under `docs/` + `workspace/current/TASK_LEDGER.yaml` | Any experiment / campaign / data work |
| Comprehension | `workspace/current/COMPREHENSION.md` | Before execution; refresh via `skills/project-comprehension.md` |
| Live pointer | `workspace/current/NEXT_ACTION.yaml` | Focus only — never overrides ledger |
| Operating / status | `docs/MASTER_PLAN.md` | Background; superseded by experiment plan + ledger when those exist |
| Indexed objects | `H_*` / `EXP_*` / … | Prefer `nav` / `project_api` |

```bash
python3 tools/plan_pointer.py
python3 tools/nav.py resolve master_plan
python3 tools/nav.py resolve next_action
python3 tools/nav.py resolve consult_plan
```

## When mandatory

Run **before** acting if the task is: learning, experiment design, claim/result write, paper writing, OS/skill evolution, or “what next?”.

Skip only for pure nav/integrity/typo fixes with **no** knowledge or protocol change.

## Checklist

1. Read `workspace/current/TASK_LEDGER.yaml` (**authoritative** task state; `skills/task-ledger.md`).
2. Read `workspace/current/COMPREHENSION.md` and run a fresh four-part pass if starting work (`skills/project-comprehension.md`).
3. Read the instance plan sections cited by the next unfinished task.
4. Read `workspace/current/NEXT_ACTION.yaml` (pointer only — fix it if it disagrees with the ledger).
5. `python3 tools/project_api.py context --task <intent>`. Read **only** listed skills.
6. If `os.pack` is `pipeline`: `skills/pipeline-entry.md` when listed. If `paper` / writing: `skills/paper-entry.md`. If a new meeting file appeared: `skills/meeting-record.md`.
7. Autoresearch / micro-loops: also `skills/autoresearch.md` + `skills/experiment-loop.md`.
8. End: update TASK_LEDGER + COMPREHENSION + NEXT_ACTION if needed; dense Change Report with `plan_ref`; integrity.

## Anti-patterns

- Treating “I glanced at README” as plan consult.
- Pre-reading all `skills/*.md`.
- Editing MASTER_PLAN next-actions without updating `NEXT_ACTION.yaml`.
- Treating a toy/prototype run as task completion (`validation_of` ≠ `done`).
- Letting `NEXT_ACTION.yaml` and `TASK_LEDGER.yaml` disagree (ledger wins).
- Executing without the comprehension pass (skipping the plan-vs-code diff is how a slice became "the task").
