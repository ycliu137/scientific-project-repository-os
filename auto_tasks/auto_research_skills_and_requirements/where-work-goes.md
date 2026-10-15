# Requirements — where files go

You are executing this task. This section is part of the assignment.

| What | Where |
|------|--------|
| Task statement, including design changes and a redo | Markdown **directly in** `auto_tasks/<this-task>/`. Git history keeps the earlier wording |
| Progress, state, handoff, design log, audit | `auto_tasks/<this-task>/auto_docs/`. Create the folder on the first such write |
| Stage gate | `auto_tasks/<this-task>/auto_docs/reviews/<stage_id>/`. COMPLETE only after `tools/check_stage_gate.py` exits 0 |
| Report | `tex_docs/<topic>/<topic>.tex` and the compiled PDF |
| Done / not-done for the campaign | The task ledger, with evidence. This folder does not replace the ledger |
| Bulk outputs | The instance's run tree, cited by path from `auto_docs/` and the report |

Do not put the report under `auto_tasks/`. Do not put a new handoff beside
the task statement. Files already sitting beside an older brief stay where
they are until that task moves them.

A redo stays in this folder, updates the task statement, and writes a **new**
report topic. Earlier reports in `tex_docs/` remain as history.

The same layout is also specified in `skills/auto-tasks.md`. That file stays.
This copy is in the task so you apply the layout without looking it up.
