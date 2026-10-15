# Requirements to insert into an auto-research task

Files in this folder are written so they can be **pasted into a task
statement**. The executing agent then sees the rules inside the assignment,
instead of having to remember a skill it read at session start.

The same rules also live under `skills/` (`skills/auto-tasks.md`,
`skills/multi-agent-research.md`, `skills/autoresearch.md`,
`skills/long_running_research_protocol.md`, `skills/compute-hosts.md`).
Those copies stay. They are the repository contract. This folder is the
reminder copy. Do not delete the `skills/` copies because this folder exists.

If a pasted requirement and a `skills/` file disagree, follow the stricter
one. The task's scientific objective does not cancel these requirements.

## What to insert

When you assign a task, put the text of these files into
`auto_tasks/<task_folder>/<brief>.md` (or tell the agent that the brief
includes them by path, and quote the path in the brief).

| Always insert | Why |
|---------------|-----|
| `always-requirements.md` | The short list agents skip: where files go, no self-approval, disk is memory, do not invent results, keep the session alive until every assigned task is finished, and compact finished detail inside that session when the context gets long |

Also insert every file the task can violate:

| Insert when the task… | File |
|------------------------|------|
| is substantial (new science, a grid, a redo) | `independent-review.md` (the stage gate; COMPLETE requires `tools/check_stage_gate.py` exit 0) |
| creates or revises the brief | `writing-a-task-brief.md`, `where-work-goes.md` |
| runs long enough that a crash must be resumable | `execution-records.md` |
| reuses code or scales a roster | `audit-before-scale.md` |
| designs leaves, splits, or OOD | `roster-and-splits.md` |
| defines a metric, a loss, or a table | `metrics-and-numerics.md` |
| submits cluster jobs | `cluster-campaigns.md` |
| must produce a report | `report-verification.md` |
| shares the repo with another agent | `concurrent-sessions.md` |

A substantial task inserts **all** of them. A trivial edit inserts
`always-requirements.md` only.

These files stay in this folder as the source. The task brief contains a
copy or an explicit include. Do not leave the requirements only in `skills/`.
