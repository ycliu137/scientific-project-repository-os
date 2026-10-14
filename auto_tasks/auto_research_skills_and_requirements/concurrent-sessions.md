# Requirements — other agents in this repo

You are executing this task. This section is part of the assignment. Other
agents may be in this same clone. You and they stay on the current branch
and do not replace each other's files.

## Stay on the branch you found

Do not switch branches and do not open a second worktree of this clone to
"isolate" a task. A checkout changes the files every other agent in this
directory is reading. Isolation is by **which files you edit**, not by
moving HEAD.

If two edits would conflict, copy the file this task needs and change the
copy. A script another campaign owns, including one with a hard-coded
setting that blocks this task, is not yours to edit.

## Commits

- Commit when a stage is done. Do not accumulate the session's work into one
  commit at the end.
- One commit, one reason, in English, saying why.
- `git status` and `git diff` first. `git add` the files this task changed.
  Do not `git add -A` or `git add .`.
- Do not commit `.pi/`, secrets, large outputs, another agent's uncommitted
  edits, or a change that belongs to a different stage.
- Push only your commits. Do not force-push. Do not `git reset` or `git
  stash` in a way that drops another agent's work.
- If a pull is blocked by someone else's uncommitted files, stop at the
  local commit. Do not touch those files in order to push.
- Record the commit hash in the design log entry for that stage.

Code the task runs lives in this project's repositories. Copy a needed
routine in and modify the copy. Do not import from a read-only upstream
checkout, and do not commit into that upstream.

## Shared cluster account

Another task holding the account's device cap is not a reason to withhold
a legal submission, and it is not a reason to run a GPU workload on CPU.
Submit and leave a genuine queue pending (`cluster-campaigns.md`).

## Shared files

Do not let two agents edit the same source file, the same report, or the
same state file. Subagents are for an independent audit, a recomputation,
or a draft. They report back; they do not rewrite the brief's objective.

## Disk budget

If the brief sets a storage cap, raw intermediates may be deleted after the
parameters needed to regenerate them are recorded (config, seeds, code
hash, job id). A result that cannot be regenerated is not an intermediate.
