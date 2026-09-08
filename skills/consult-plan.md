# consult-plan.md — Plan as procedure (not homework dump)

Do **not** require a full read of every design note every session.

## Document layers

| Layer | Path | When to open |
|-------|------|----------------|
| Constitution | `SKILL.md` | Always (Bootstrap) |
| Operating plan | `docs/MASTER_PLAN.md` | Learning / evolution: next-actions section |
| Live pointer | `workspace/current/NEXT_ACTION.yaml` | Every learning session |
| Indexed objects | `H_*` / `EXP_*` / … | Prefer `nav` / `project_api` |

```bash
python3 tools/nav.py resolve master_plan
python3 tools/nav.py resolve next_action
python3 tools/nav.py resolve consult_plan
```

## When mandatory

Run **before** acting if the task is: learning, experiment design, claim/result write, paper writing, OS/skill evolution, or “what next?”.

Skip only for pure nav/integrity/typo fixes with **no** knowledge or protocol change.

## Checklist

1. Read `workspace/current/NEXT_ACTION.yaml`.
2. Open `docs/MASTER_PLAN.md` for the live section (not the whole archaeology).
3. `python3 tools/project_api.py context --task <intent>`. Read **only** listed skills.
4. If `os.pack` is `pipeline`: `skills/pipeline-entry.md` when listed. If `paper` / writing: `skills/paper-entry.md`. If a new meeting file appeared: `skills/meeting-record.md`.
5. End: update NEXT_ACTION if needed; dense Change Report with `plan_ref`; integrity.

## Anti-patterns

- Treating “I glanced at README” as plan consult.
- Pre-reading all `skills/*.md`.
- Editing MASTER_PLAN next-actions without updating `NEXT_ACTION.yaml`.
