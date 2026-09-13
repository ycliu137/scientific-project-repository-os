# project-comprehension.md — mandatory pre-execution comprehension pass

Executing without understanding the whole project is how a **slice gets
recorded as the whole** and a **toy run gets recorded as done**. This skill
makes a comprehension pass a **gated step**, not self-discipline, and separates
**audit** (read-only) from **execution** (write).

## When mandatory

- Before **any** experiment / pipeline / evolution / data campaign work.
- On **every cold start** (with `skills/task-ledger.md`).
- After any **interruption** or unexpected result.

No comprehension record → do not start executing.

## Record

`workspace/current/COMPREHENSION.md` — durable fruit of the pass. Cold-start
reads it right after `TASK_LEDGER.yaml`.

## The four-part pass (do all four; keep each short and factual)

1. **Authority pass** — list authoritative files for this task and what each
   says (`SKILL.md`, the instance plan under `docs/`, `TASK_LEDGER.yaml`, any
   data/cluster runbooks the instance defines). Flag **contradictions**.
   `NEXT_ACTION.yaml` / stale status sections are pointers/background, **not**
   authority when a ledger + experiment plan exist.
2. **Data / inventory pass** — what actually **exists** (datasets, sizes,
   QC/provenance, caches, artefacts), not what *should* exist. Name shortfalls.
3. **Plan-vs-code diff** — does the **executable** match the plan? List every
   divergence (e.g. a driver hardcoding a toy grid while the plan specifies a
   larger one). This is the check that catches "slice = whole".
4. **Scope decision** — full vs slice, and **why**, written down. A slice is
   allowed only if labelled as a slice (ledger keeps the real task open).

Write the four sections into `COMPREHENSION.md` (overwrite; keep current).

## Execution vs audit separation

- Do the pass **read-only** first: read, diff, inventory — no writes except the
  record and, if needed, a Change Report.
- For independence, the pass **may** be delegated to a **read-only subagent**
  (fresh context) that returns the four sections; the parent then continues.
  Delegation is optional; the inline read-only pass is the default.
- Never let audit findings silently change scope — record them, then act.

## Automatic mode switch — do NOT stop

Switching audit → execution is **automatic and continuous**. After the pass:

1. Update `COMPREHENSION.md` (and `TASK_LEDGER.yaml` if state changed).
2. Proceed **directly** to the next unfinished ledger task in the same session.
   Do **not** pause to ask "shall I proceed?" when nothing is blocked.
3. Stop for the user **only** on a genuine blocker or real ambiguity the plan
   cannot resolve — and even then, state options and a recommendation.

## Anti-patterns

- Anchoring on the nearest writable artifact (`run_*.py`) instead of the plan.
- Treating a slice / toy / smoke run as the whole task.
- Skipping the pass "because the task looks small".
- Asking the user to confirm an unblocked next step (breaks continuity).
- Editing the plan/acceptance to match what was actually run.
