# Requirements — execution records

You are executing this task. This section is part of the assignment. These
files live in this task's `auto_docs/`. They are not a second task
statement. The brief stays the design. These files are what happened. A
session transcript is not a substitute.

A new session reads the latest state or handoff, then checks the live jobs
and the artefacts. It does not reconstruct the campaign from the conversation.

## Which file is which

| File | Role | How it grows |
|------|------|----------------|
| `STATE.md` (or `<campaign>_STATE.md`) | Where the work stands: stage, facts that survived a check, known problems, next actions, canonical paths | Rewrite the status sections. Do not append a transcript |
| `HANDOFF_*.md` | What a fresh session must do first | New file when the session boundary is real. The top of the file is the blocker and the rule, then what has not changed |
| `DESIGN_LOG.md` | What was actually submitted and what came back | Append-only. Job id, config, outcome, and the fix |
| `AUDIT_*.md` | A read of existing code, data, or a metric before reuse | One question per audit. Cite line ranges and inputs. End with what may be reused and what must not |
| `STATUS_*.md` | A session snapshot when STATE would become a diary | Goal, owner decisions locked this session, done, running, settled science, defects, next |

Older tasks may still have these files beside the brief. Leave them. New
ones go in `auto_docs/`.

## A handoff opens with the action

The first screen answers:

- what failed or what is blocking, with the job id, the state, and the error
- the rule that prevents the same failure (device paired with environment,
  metric orientation, a knob that was never applied)
- which jobs are running, pending, or finished
- which scientific conclusions still stand
- the next command or the next decision
- paths to the brief, the state file, the report, and the manifests

A narrative of the session belongs below that, or in the design log.

## A design log entry

For each block of work record:

- what was submitted (command or job-body path, hash if it matters)
- job identifiers and the queue
- what returned (exit, artefact present or absent, the metric)
- whether the failure was science, an implementation bug, or the environment
- the fix and the resubmit identifiers
- what was deliberately not resubmitted because its outputs already existed

## What "done" in these files means

A stage is done only when its pass rule in the brief holds and the artefact
is cited. "The job finished" is not done. A scheduler success code is not
done. Point at the file that was checked.

A fitted model is cited only after a fresh process reloads the saved
directory and matches the in-memory predictions on training rows and
held-out rows. A prediction cache for the training table does not satisfy
that check (`always-requirements.md`).

When a historical conclusion is invalidated, write what it is now evidence
of, and what must be redone. Do not delete the old record.

## Context

The session keeps the open stage, the frozen constraints, and one line per
completed gate with its path. Verbose debugging stays in the design log.
**Keep this session alive until every assigned task is finished.** Do not
end it, and do not hand the remaining work to another session, while any
assigned task remains. Waiting for a job is not a reason to stop. Record
the job so a crash can resume, then keep working in this same session
(`skills/long_running_research_protocol.md`).
