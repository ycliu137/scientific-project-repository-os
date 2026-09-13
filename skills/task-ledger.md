# task-ledger.md — authoritative per-campaign task state machine

The **task ledger** is the single source of truth for "what tasks exist, what
state each is in, and what counts as done". It exists so a toy / prototype /
smoke run can **never** be mistaken for the real task, and so a cold-start
agent immediately knows what is finished, interrupted, or still open.

## File

`workspace/current/TASK_LEDGER.yaml` (per instance; kept in git).

## When mandatory

- **Before** starting any multi-step experiment or campaign: write tasks from the
  plan's acceptance criteria. No ledger → do not run the campaign.
- **After** every task transition (start / interrupt / done): update the ledger
  in the same change as the evidence.
- **Every cold start**: read the ledger (via `plan_pointer` / directly) before
  trusting `NEXT_ACTION.yaml`.

## States

| State | Meaning |
|-------|---------|
| `not_started` | no work begun |
| `in_progress` | started, not finished |
| `interrupted` | started then stopped mid-way; `resume_notes` says how to resume |
| `done` | acceptance criteria met **and** evidence present |

Toy / smoke / prototype work is **not** a fifth state. Record it in the
optional field `validation_of` on a still-unfinished task. Never set
`state: validation`.

Each task also carries:

```yaml
- id: T-xx
  title: <what>
  plan_section: <which section of the plan defines it>
  acceptance: <the plan's "done when">
  state: not_started | in_progress | interrupted | done
  validation_of: <optional: what a prototype exercised — does NOT satisfy the task>
  evidence:        # required for state=done
    - <change report path>
    - <settings/params/artifact paths>
  settings: {}     # run-identifying parameters for reproducibility
  resume_notes: <optional: how to resume if interrupted>
```

## Machine gate

`tools/check_project.py` enforces part of this: a missing ledger is a WARN;
`state: done` without non-empty `evidence` is an **ERROR**; `done` +
`validation_of` together is an **ERROR**.

## Prompt preamble (fixed wording)

Before acting on an experiment/campaign, restate:

1. **Authoritative files:** the instance experiment/operating plan +
   `workspace/current/TASK_LEDGER.yaml`. `NEXT_ACTION.yaml` is a pointer only.
2. **Forbidden:** recording a toy/smoke/prototype run as `done`; use
   `validation_of` only.
3. **Next unfinished task IDs:** from the ledger; work those in order; update
   ledger + evidence when each is done.

## The hard rule (prevents "toy = done")

1. A task may be `done` **only** when `acceptance` is met and `evidence` is
   non-empty.
2. A run that only exercises mechanics is `validation_of`, never `done`.
3. Do not edit a `done` task's `acceptance` to match what was run. Plan changes
   are separate Change Reports.
4. If `NEXT_ACTION.yaml` disagrees with the ledger, the **ledger wins**.

## Reproducibility

Every `done` task should record in `settings` the parameters that identify the
run (env, seeds, grid/config, model/hyperparameters, output paths) so the task
can be summarized from the ledger alone.

## Cold-start handoff

Read `SKILL.md` → `MAP.md` → `plan_pointer.py` → **`TASK_LEDGER.yaml`** →
`COMPREHENSION.md` → listed skills. Resume `interrupted` from `resume_notes`.

## Anti-patterns

- Marking a phase complete because a sub-scale run produced numbers.
- Recording a run only in a report without updating the ledger.
- Two sources of truth (NEXT_ACTION says done, ledger says in_progress).
- Editing acceptance after the fact to match what was run.
