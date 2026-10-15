# long_running_research_protocol

**Persist everything important; contextualize only what is currently necessary.**

Use this protocol for any campaign that can outlive one agent session: BSP,
omega, covprior, feature autoresearch, multi-day cluster chains, or any loop
that would otherwise keep its memory inside a conversation. It is generic.
Campaign names change; the layers do not.

Related: `skills/task-ledger.md` (done-gate), `skills/project-comprehension.md`,
`skills/autoresearch.md`, `skills/experiment-loop.md`,
`docs/design/LONG_RUNNING_RESEARCH.md`. Skeletons:
`docs/templates/execution_plan.yaml`, `docs/templates/execution_record.yaml`,
`docs/templates/experiment_registry.csv`.

## What this replaces

A long session is short-term working memory. The repository is the durable
store. **Keep this session alive until every assigned task is finished.**
Do not end it, and do not hand the remaining work to another session, while
any assigned task remains. Write state to disk from the start so that, if
this session dies, the campaign still knows where it is, why it is there,
and what is next. That record is crash insurance. It is not a reason to stop.

Do this from the **start** of the campaign. Do not wait until the context is
already huge. Compact finished detail inside this same session, then continue:

```
Task → checkpoint → compact → next task
```

A fresh session is only the recovery path after this one has already died.
It loads the disk layers below. It does not replay the old conversation, and
it does not treat the death as the end of the task.

## Three layers

| Layer | Lives | Role | Evict from active context? |
|-------|--------|------|----------------------------|
| 1. Authoritative state | contract, execution plan, campaign state, task ledger | What is true, what is next, what "done" means | Never, because of context pressure |
| 2. Evidence | `workspace/history/<campaign>/` and the experiment registry | How a finished task was done | Yes, after the one-line outcome is written |
| 3. Working set | the current session | The open task only | Yes, on complete and on handoff |

### Layer 1 — authoritative state

Create these **before** the first long task runs. If a campaign already has a
contract or state file, keep that path and point the plan at it. Do not rename
live files to match an example.

| Piece | Typical path | Authority |
|-------|----------------|-----------|
| Contract | instance-defined (`EXPERIMENT_CONTRACT.yaml`, a design doc, or both) | What correct means. Never rewrite it to match a slice that was run |
| Execution plan | `workspace/current/<campaign>_EXECUTION_PLAN.yaml` | Full task DAG: ids, dependencies, status, context policy |
| Campaign state | `workspace/current/<campaign>_STATE.yaml` | Compact facts: gates, jobs, leaves, resume pointer. Not a transcript |
| Task ledger | `workspace/current/TASK_LEDGER.yaml` | OS done-gate (`skills/task-ledger.md`) |

One campaign for the whole repo may drop the `<campaign>_` prefix
(`EXECUTION_PLAN.yaml`, `STATE.yaml`).

Plan statuses are operational. Ledger states stay the machine gate. Keep them
in agreement:

| Plan `status` | Ledger `state` |
|---------------|----------------|
| `pending` | `not_started` |
| `in_progress` | `in_progress` |
| `blocked` | `not_started` if never started; `interrupted` if work stopped |
| `interrupted` | `interrupted` |
| `completed` | `done` (acceptance met **and** evidence non-empty) |

If they disagree, the **ledger wins** on done / not-done. The plan wins on
dependency order. Fix the stale file in the same change. Toy, smoke, and
prototype runs stay `validation_of` on the ledger. They never flip a task to
`completed` / `done`.

Minimum plan shape (full skeleton in `docs/templates/execution_plan.yaml`):

```yaml
campaign: <name>
contract: <path>
state: workspace/current/<campaign>_STATE.yaml
ledger: workspace/current/TASK_LEDGER.yaml
tasks:
  - id: A0-001
    task: validate leaf provenance
    depends_on: []
    status: in_progress
  - id: A0-002
    task: complete smoke
    depends_on: [A0-001]
    status: pending
  - id: A0-003
    task: run A0-FULL
    depends_on: [A0-001, A0-002]
    status: blocked
```

A cold agent that has forgotten the conversation must still be able to read
this DAG and answer: where are we, why, what is unblocked.

### Layer 2 — evidence

Do not keep growing `STATE.yaml` with logs. Each task gets its own execution
record:

```
workspace/history/<campaign>/<task_id>_<slug>.yaml
```

Required fields (skeleton: `docs/templates/execution_record.yaml`):

- `task_id`, `status`, `started_at`, `completed_at`
- `hypothesis_or_goal`
- `actions`, `findings`, `files_changed`
- `tests` (`command`, `result`)
- `artifacts` (`path`, `sha256` when the file is an evidence blob)
- `decision` (`outcome`, `reason`)
- `issues_found`, `commit`
- `validation_of` when the run was only a smoke / toy / prototype

Point the ledger `evidence` list and the plan task `evidence` at this file.
History is archived, not deleted. Commit the record. Bulk run trees stay where
the instance already stores them; the record holds paths and hashes.

### Layer 3 — working set

The session that is executing one task needs only:

- the contract (or the sections that bind this task)
- the execution plan
- the campaign state
- the current task spec and its dependency **summaries** (outcome + evidence path)
- the code and logs relevant to the open issue

It does not need resolved debugging from earlier tasks: dropped flags, old job
ids, how a marker bug was found. Those stay in the history file and are
re-read only when an investigation actually needs them.

## Context lifecycle

Default policy (copy onto the plan; override per task only when needed):

```yaml
context_policy:
  on_start:
    load:
      - contract
      - current_state
      - task_spec
      - dependencies_summary
  during:
    retain:
      - current findings
      - current logs
      - relevant code
  on_complete:
    persist:
      - detailed execution record
      - artifacts
      - decisions
      - tests
      - issues
      - commit
    active_context_keep:
      - task_id
      - final outcome
      - important decision
      - unresolved dependencies
      - evidence path
    active_context_evict:
      - exploratory logs
      - failed intermediate attempts
      - verbose command output
      - resolved debugging details
```

`active_context_evict` means drop from the **session**, not from disk.
Completed detail remains in the execution record.

After each completion, leave one line in the plan `resume.completed` list:

```text
A0-001 COMPLETE — cross-leaf collision caused by XXX; fixed in commit XXX; regression tests PASS; evidence: workspace/history/<campaign>/A0-001_leaf_provenance.yaml
```

## Checkpoint, compact, handoff

On **task start**: set plan `in_progress` and ledger `in_progress`. Record
`started_at`. Load only `on_start.load`.

**During** a long task (multi-hour job, multi-day queue): update campaign
state and, if the session might die, write an interim history record with
`status: in_progress` and `resume_notes`. Do not evict the open working set
yet.

**Keep this session alive until every assigned task is finished.** A pending
or running job is unfinished work in this same session. Before or at
submission, persist the job id, the command or job-body path and its hash,
the code and input hashes, the output path, and what success will look like,
so a crash can be resumed. Then keep working here: do the next piece that
does not need this result, and continue as soon as the job returns. Do not
end the session, and do not hand the campaign to another session, while any
assigned task remains. A later session must still be able to inspect the job
without the old transcript if this one dies. Scheduler "state unavailable" means
reconcile against the artefacts, not "the job finished." A scheduler success
code alone is not scientific success. A directory that holds a fitted model
is a checkpoint only after a fresh process reloads that directory alone and
reproduces the fit-time predictions (`skills/autoresearch.md`).

A gate is a decision rule. If it passes and the plan already names the next
step, continue. If it fails and the plan names the branch, follow that branch.
Ask the owner only when the result creates a scientific choice the plan does
not cover. Completing a task is not a reason to stop when the plan already
says what comes next.

On **task complete**, in the same change:

1. Write the execution record.
2. Update campaign state (facts only).
3. Set plan status and ledger state together, with evidence paths.
4. Append the one-line outcome to `resume.completed`.
5. Evict `active_context_evict` from the session and continue to the next
   unblocked task.

**Resume record.** Write `resume` on the execution plan (and a short mirror
on the state file) as you go, so a crash can be resumed. Do not end the
session in order to write it. Keep this session alive until every assigned
task is finished.

```yaml
resume:
  current_task: A0-002
  next_unblocked: A0-002
  open_issues: []
  completed:
    - "A0-001 COMPLETE — ...; evidence: workspace/history/<campaign>/A0-001_leaf_provenance.yaml"
```

A fresh session loads, and only loads:

1. contract
2. execution plan
3. campaign state
4. current task spec
5. dependency summaries (the one-line outcomes and their evidence paths)
6. history files **only** for issues that are still open

Then it continues. It does not ask the previous conversation to survive.

## Experiment registry

Feature autoresearch may run tens or hundreds of experiments. The conversation
must not be the list of exp01 … exp87.

Keep an append-only registry (CSV is the portable default; a parquet mirror is
optional):

```
workspace/experiments/<campaign>_registry.csv
```

Columns (`docs/templates/experiment_registry.csv`):

`experiment_id`, `hypothesis`, `parent`, `config`, `seed`, `commit`, `metrics`,
`ood_metrics`, `decision`, `artifact_paths`, `evidence_path`

The working set for the next experiment is:

- the current Pareto frontier, or the current best if there is one metric
- the few experiments that motivate the next hypothesis
- the next hypothesis itself

Failed experiments stay in the registry. Re-read rows when a comparison needs
them. Do not paste the full registry into the session.

Registry rows do not replace the ledger. A campaign task is `done` only under
`skills/task-ledger.md`. A micro-loop (`.auto/` or an external agent) still
re-enters through the ledger, a Change Report, and, when the loop is a real
search, a registry row (`skills/autoresearch.md`).

## Anti-patterns

- Treating the conversation as the campaign memory.
- Deleting history to free context. Archive, summarize, evict from the session.
- Stuffing logs, job transcripts, or failed attempts into `STATE.yaml`.
- Opening a fresh session without writing `resume` first.
- Waiting for a multi-million-token session before the first checkpoint.
- Loading the whole registry, or every completed history file, "just in case".
- Marking plan `completed` from a smoke run.
- A second done-authority that disagrees with `TASK_LEDGER.yaml`.
- Ending the session, or handing the campaign to another session, before every assigned task is finished. A pending or running job is unfinished work in this same session.
- Treating a scheduler success code as the scientific result.
