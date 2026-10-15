# auto-tasks.md — where an auto-research assignment lives

Use this when an owner assigns agent-driven research, when a session resumes
one, and when the design of that task changes. Companion:
`skills/autoresearch.md`, `skills/multi-agent-research.md`,
`skills/tex-docs.md`.

`auto_tasks/` is the assignment surface. It is where a task is designed, kept,
looked up later, revised, and redone. It is not a results dump and not a
report.

## Layout

One task, one folder: `auto_tasks/<task_folder>/`.

| What | Where |
|------|--------|
| Task statement | Markdown files **directly in** `auto_tasks/<task_folder>/`. This is the design record. Revise these files in the same folder when the design changes, the task is updated, or the task is redone. Git history keeps the earlier wording. |
| Progress and handoff during execution | `auto_tasks/<task_folder>/auto_docs/`. State, plans, audits, and handoffs written while the task runs go here. Create the folder on the first such write. |
| Stage gate for a substantial stage | `auto_tasks/<task_folder>/auto_docs/reviews/<stage_id>/`. Four reviews, the verifier, parallelism evidence, and `gate_result.txt` from `tools/check_stage_gate.py` (`skills/multi-agent-research.md`). |
| Task report | `tex_docs/<topic>/<topic>.tex` plus the compiled PDF (`skills/tex-docs.md`). A redo adds a new report topic and leaves earlier reports in `tex_docs/` as history. |

Read the task-statement markdown before executing. Resume from `auto_docs/`
when a previous session left a handoff. Write results into the `tex_docs/`
report for that task.

Campaign truth still re-enters the ledger, evidence records, and a Change
Report (`skills/autoresearch.md`, `skills/task-ledger.md`). The task folder
does not replace `TASK_LEDGER.yaml`.

## What belongs in the task statement

Write the statement before the large run, and keep it current:

- the question, and which decision each outcome would change
- frozen inputs, assumptions, and what must not be changed mid-run
- acceptance criteria, fixed before seeing the result
- expected artefacts and where the report will go
- compute placement and any instance budget or queue rule

A criterion written after the result is a rationalisation, not a task.

## During execution

- New progress, state, and handoff files go in that task's `auto_docs/`.
- Files already sitting beside an older task statement stay where they are
  until that task moves them. Do not reshuffle history to match this layout.
- Update the on-disk state when the stage changes. A stale checklist in the
  session is not the campaign state.
- Do not put the scientific report under `auto_tasks/`.

## Redo

A redo stays in the same task folder. Update the task statement there, keep
prior reports in `tex_docs/`, and record what was kept, what was discarded, and
why. Open a new folder only for a new task.

## Requirements inserted into a task

`skills/` remains the contract. The same rules are written again, in a form
that is pasted into the task statement so the executing agent sees them, in
`auto_tasks/auto_research_skills_and_requirements/`. Insert
`always-requirements.md` into every assignment, and the other files in that
folder when the task can violate them. Do not delete the `skills/` copies.
