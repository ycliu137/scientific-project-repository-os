# Requirements — always in force

You are executing this task. This section is part of the assignment. Follow
it. Do not treat it as optional background.

The same rules are also in `skills/`. Those files stay. This copy is here so
you see the rules inside the task.

## Where the work goes

- The task statement is the markdown **in this task folder**. It is the
  design. When the design changes or the task is redone, edit that markdown
  here. Do not open a second folder for a redo.
- Progress, state, audits, and handoffs go in this task's `auto_docs/`.
  Do not drop them beside the task statement.
- The report goes in `tex_docs/<topic>/` as `.tex` and a compiled `.pdf`.
  A markdown summary does not replace it. A redo adds a new report and leaves
  the old one in place.
- Campaign truth also goes to the task ledger, an evidence record, and a
  Change Report. A session transcript is not the record.

## Do not approve your own work

On a substantial task, plan review, implementation, specialist review
(mathematics, code, results), and final acceptance are different duties.
You do not accept work you implemented. Final acceptance is exactly one of
**PASS**, **FAIL**, or **INCONCLUSIVE**. FAIL or INCONCLUSIVE means the task
is not done. A green test suite is not scientific correctness.
Details: `independent-review.md` in this folder. Insert it for any
substantial task. A substantial stage is not COMPLETE until
`python3 tools/check_stage_gate.py --stage-dir auto_tasks/<task_folder>/auto_docs/reviews/<stage_id>`
exits 0. Your own review, a green test suite, and a long context do not
replace that exit.

## Before you scale

State which decision the run will change. If no outcome would change the
next step, do not run it. Confirm the switch you depend on actually changes
the artefact, on one unit, before you build the roster. A small test checks
that the code runs. It does not answer the scientific question and its
numbers do not enter the headline table.

## The session stays alive

**Keep this session alive until every assigned task is finished.** Do not
end it. Do not hand the remaining work to another session. Do not stop in
the middle.

A running or pending job is unfinished work inside this same session. Record
the job id, the command, the provenance, the output path, and what success
looks like, so a crash can be resumed. Then keep doing every next step that
does not need that result, and continue the moment the job returns. The
record is crash insurance. It is not a reason to stop.

## When the context gets long

The session has a context limit. That limit is not a reason to end the
session or to open a new one. Remove finished detail from the session, then
continue in this same session.

After a stage is on disk:

- Keep in the session: the open stage, the frozen constraints, and one line
  per completed stage with its evidence path.
- Drop from the session: exploratory logs, failed intermediate attempts,
  verbose command output, and debugging that is already resolved.
- Those details stay in `auto_docs/` and the evidence record. Removing them
  from the session does not delete them from disk. Do not delete history to
  free context.

Do this as the context grows, then continue the next assigned task. A new
session is only the recovery path after this one has died
(`skills/long_running_research_protocol.md`).

## A fitted model is usable before it is saved

A fitted model is complete only when a later process can apply it to new
inputs. Training that cannot be reloaded is not finished. Do not mark that
directory saved.

Before the directory counts as a checkpoint, it contains everything that
process needs. The later process does not recover missing pieces from the
training table, the trainer source, or a retrain:

- The fitted object in a form a loader can run. A weight file without the
  architecture required to rebuild the network is not that object. A fitted
  estimator counts only when the loader can call it.
- Every transform fit on the training split, including location, scale, and
  the exact column order after unusable columns were dropped. A head fit on
  its own rows carries its own transform.
- Every constant that turns the raw output back into the quantity the next
  stage consumes, and a statement of whether the objective applied a
  transform inside the model or on the target.
- The identity of the fit: family, objective, seed, split, and the other
  knobs that change the function.

After writing the directory, a fresh process reads only those files,
predicts on training rows and on held-out rows, and matches the predictions
produced in memory at fit time. If the reload fails or the numbers disagree,
the fit is not complete.

A file of predictions on the training table is a cache of that table. It is
not the model. A loader that implements only some families is not a reason
to leave the other families unusable. Every family and every objective the
task trained meets the same bar.

## While you run

- Write the acceptance rule before you see the result.
- Persist the scientific object the next stage needs, not only a summary
  metric. A fitted model meets the reload rule above before it is saved.
- A failed arm is a result. Record what the evidence supports and stop.
  Do not replace it with a successful-looking output. Do not fabricate a
  number. If an artefact is missing, say so.
- A job that exits 0 is not a result. The brief's endpoint is the result.
- Update the on-disk state when the stage changes. A checklist only in the
  conversation is not the state.
- Continue to the next step when the brief already names it. Ask the owner
  only for a scientific choice the brief does not cover, an irreversible
  action, or an unresolved high-impact conflict.
- Do not edit another lane's files. Copy a script you need to change.
- Another task holding the GPU cap is not a reason to skip a legal submit,
  and it is not a reason to run a required GPU workload on CPU.

## If the session dies

Do not end it yourself while any assigned task remains. If it dies anyway,
the disk record must be enough to resume: what is in flight, the rule that
prevents repeating a known failure, which jobs are live, which conclusions
still stand, and the next action. A recovery session reads that file and
continues until the remaining tasks are finished. It does not treat the
death as the end of the task.
