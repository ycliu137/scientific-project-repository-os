# Requirements — cluster campaigns

You are executing this task. This section is part of the assignment.
Instance runbooks hold the exact scheduler syntax (`skills/compute-hosts.md`).
That skill stays. Follow this copy for how the campaign is run. Do not skip
it because you already know a submit command.

## Before the wave

1. Pilot one unit on the intended device.
2. Record wall time, memory, and the environment that actually worked.
3. Size the resource request from that measurement. An oversized wall time
   or memory request is a common reason a job stays pending.
4. Preflight imports and device compatibility in the job body, so a mismatch
   fails in seconds rather than after the expensive stage.
5. Pair the device class with the environment that contains both the right
   GPU architecture and the extra packages that stage imports. Omitting the
   device pin makes the landing host a coin flip.

## Submit

- One resource unit per job unless the brief says otherwise. Fan out; do not
  pack the campaign onto one device.
- Persist, at submission: job id, command or job-body path and its hash,
  code and input hashes, output path, and the success criterion. A later
  session must resume without the old transcript.
- The cluster tree is a separate checkout. Sync the files the job needs.
  Cluster git HEAD is not provenance of the working tree.
- Idempotency has two checks: the queue, and the artefacts on disk. Either
  can fail silently (counted the wrong unit, matched no path). Confirm both
  before skipping and before launching a duplicate.
- If a stage's outputs already exist, resubmit only the missing units.

## Pending

A long wait is a diagnosis (`skills/multi-agent-research.md`).

- Resources are occupied, or the queue is backed up. Leave the job pending.
  Another task holding the account cap is not a reason to skip the submit,
  and it is not a reason to run the workload on CPU when the brief requires
  the GPU queue.
- The submission is faulty: never accepted, held, waiting on a dependency
  that will not finish, aimed at an unavailable partition, or pending for a
  reason waiting will not clear. Fix and resubmit. Do not wait that out.

## After the job

Exit status, log tail, artefact present, and the recorded metric. Exit 0
with no artefact is a failure. A scheduler success code is not the
scientific result.

Separate three causes before changing the method: the hypothesis, an
implementation bug, and the environment (wrong device image, missing
package, wall time too short for a coefficient that is genuinely slower).

## Keep the session alive

**Keep this session alive until every assigned task is finished.** A
submitted job is unfinished work inside this same session, not a finished
stage and not a reason to end the session or to hand the work off. Record
the job id and the success criterion, update `auto_docs/` when the stage
changes, do the next piece that does not need this result, and pick the job
up the moment it returns. Stay in this session until the brief's remaining
tasks are done.
