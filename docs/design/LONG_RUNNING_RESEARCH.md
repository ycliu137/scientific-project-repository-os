# LONG_RUNNING_RESEARCH — disk state, short working context

Status: template design. Procedure: `skills/long_running_research_protocol.md`.
Companions: `skills/task-ledger.md`, `skills/autoresearch.md`,
`docs/design/AUTORESEARCH.md`.

## Principle

**Persist everything important; contextualize only what is currently necessary.**

Agent conversation context is working memory. Repository files are the durable
store. **Keep the executing session alive until every assigned task is
finished.** Do not end it, and do not hand the remaining work to another
session, while any assigned task remains. Write the campaign to disk from
the start so a crash can be resumed. That record is crash insurance. It is
not a reason to stop.

```
Plan on disk + State on disk + Evidence on disk + Short working context
```

Not: the whole project history lives in the current conversation.

## Why a protocol, not "just open a new session"

The executing session stays alive until every assigned task is finished.
Compaction happens inside that session. A fresh session is only the recovery
path after this one has already died, and it is useless if it has nothing
authoritative to load. The protocol makes that recovery a disk write:
execution plan, campaign state, one-line outcomes, evidence paths. The write
does not end the live session.

Every long-running campaign in this OS (BSP, omega, covprior, later feature
search, and campaigns that do not exist yet) uses the same layers. Domain
science stays in the instance contract. The protocol does not name a method.

## Layers

1. **Authoritative state** — contract, `<campaign>_EXECUTION_PLAN.yaml`,
   `<campaign>_STATE.yaml`, `TASK_LEDGER.yaml`. Never dropped because the
   context window is tight.
2. **Evidence** — one execution record per task under
   `workspace/history/<campaign>/`, plus
   `workspace/experiments/<campaign>_registry.csv` when the work is a search
   over many experiments. Detailed, re-readable, not part of the working set.
3. **Working set** — contract, plan, state, the open task, and the code or
   logs that task still needs.

`archive + summarize + evict from active context`. History files stay. The
session keeps a one-line outcome and the evidence path.

## Fit with the existing host

| Already shipped | This protocol adds |
|-----------------|--------------------|
| `TASK_LEDGER.yaml` done-gate | An operational DAG (`depends_on`, `blocked`) that must agree with the ledger |
| `NEXT_ACTION.yaml` pointer | `resume` on the plan: current task, one-line completions, open issues |
| `COMPREHENSION.md` | Unchanged; still required before execution |
| `.auto/` micro-loop | Optional. Search results that matter also append to the experiment registry |
| Change Reports | Still required for contract / skill / code changes. A task record does not replace one |

Ledger states remain `not_started | in_progress | interrupted | done`.
Plan statuses `pending | blocked | completed` map onto those states; they are
not a second machine gate. `check_project` still enforces done ⇒ evidence.

## Context lifecycle

Each task declares `on_start` / `during` / `on_complete`. Completion runs
`checkpoint → compact → next task`: persist the execution record, update state
and plan and ledger, keep the one-line outcome, evict exploratory logs and
resolved debugging from the session.

A long single task (queued cluster work) writes an interim `in_progress`
record so a dead session can resume without a transcript.

## Fresh session

Load contract, execution plan, campaign state, current task, dependency
summaries. Open a history file only to investigate an unresolved issue. Do not
preload completed investigations or the full experiment registry.

For autoresearch, the working set is the Pareto frontier (or current best),
the few parent experiments that motivate the next hypothesis, and that
hypothesis. Older failures remain registry rows.

## What instances create

The template does not pre-create campaign files. First write creates:

- `workspace/current/<campaign>_EXECUTION_PLAN.yaml` (from `docs/templates/execution_plan.yaml`)
- `workspace/current/<campaign>_STATE.yaml` when the campaign has no state file yet
- `workspace/history/<campaign>/<task_id>_<slug>.yaml`
- `workspace/experiments/<campaign>_registry.csv` when experiments accumulate

Existing contract and state paths stay. The plan's `contract` and `state`
fields point at them.

## Maintainer notes

- Additive host contract. Do not require a particular agent product.
- Do not encode one agent's prompt format as the only legal resume note.
- The one-line completion format in the skill is a convention, not a parser API.
- Do not weaken `skills/task-ledger.md`: smoke is still not done.
