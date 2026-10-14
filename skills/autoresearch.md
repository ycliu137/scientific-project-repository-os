# autoresearch.md — OS host contract for autonomous research loops

Autoresearch (agent-driven propose → measure → keep/discard loops) is a
**first-class** concern of this OS: future science work will often rely on it.
The OS therefore ships a **host structure** that helps agents stay aligned with
project truth. That structure must **never** become a ceiling on what a stronger
future autoresearch agent can do.

Related: `skills/auto-tasks.md` (where the owner assignment, the execution
trace, and the report live), `skills/multi-agent-research.md` (independent
review for a substantial task), `skills/experiment-loop.md` (optional `.auto/`
mechanics), `skills/task-ledger.md`, `skills/project-comprehension.md`,
`skills/long_running_research_protocol.md` (disk plan / evidence / short context),
`skills/compute-hosts.md`, `docs/design/AUTORESEARCH.md`.

## Design principles (ordered)

1. **Help, then get out of the way.** Provide clear places for authority, task
   state, pre-execution audit, and result re-entry so agents do not lose the
   plot — then leave search strategy, tooling, and autonomy to the agent.
2. **Host without handcuffs.** Standardize *where truth lives* and *how results
   re-enter the project*. Do **not** standardize *how the agent searches*, which
   IDE/extension it uses, its prompts, stop policy, branching, or tool APIs.
3. **Forward-compatible by default.** Newer agents may be more powerful than
   anything this template foresaw. The OS must not freeze yesterday's agent UX
   into tomorrow's mandatory protocol. Prefer **additive** hooks; never require
   a particular product. If an OS convention and a capable agent conflict on
   *mechanics*, the agent may use its own mechanics — as long as **re-entry**
   (ledger / evidence / Change Report) still happens.
4. **Optional ≠ mandatory.** `.auto/`, `tools/experiment.py`, and any named
   vendor adapter are **convenience layers**. An agent that logs elsewhere, uses
   another measure harness, or auto-commits with its own policy is still in
   bounds if Layer-1 truth is respected.

| OS owns (minimum contract) | Agent owns (unrestricted) |
|----------------------------|---------------------------|
| Authority docs + task ledger + comprehension | Search strategy, idea generation, exploration depth |
| Re-entry: evidence into ledger / Change Reports / objects | Which runtime (Pi, Cursor, custom, future systems, or none) |
| Toy ≠ done; validation vs campaign | Prompts, stop/continue policy, parallelism, tool use |
| Promoting durable winners into the sibling repos | Session file layout, git automation, metrics beyond the OS CLI |

An instance **must not** require a particular autoresearch extension to be
installed. If one is present, it **plugs into** this contract; if not, humans or
agents use whatever runner they prefer and still update the ledger.

## Four layers (do not collapse)

```
1. Authority     plan + TASK_LEDGER + COMPREHENSION   (what "done" means)
2. Campaigns     pipelines / batch / cluster jobs      (ledger + scorecards)
3. Micro-loop    OPTIONAL accounting (.auto/ or agent-native)
4. Agent runtime OPTIONAL external autoresearch agent  (automation only)
```

- Layer 4 **must not** rewrite Layer 1 acceptance to match a slice it ran.
- Layer 3 **must not** claim a Layer 2 campaign is complete.
- Layer 3/4 formats are **not** sacred — only Layers 1–2 truth and re-entry are.
- Durable science still lands in `objects/`, `tex_docs/`, and Change Reports.

## How to use an assigned task

1. Read the task-statement markdown in `auto_tasks/<task_folder>/` before
   changing code or submitting jobs (`skills/auto-tasks.md`).
2. Write progress and handoffs in that folder's `auto_docs/`. Write the report
   in `tex_docs/`.
3. For a substantial task, follow `skills/multi-agent-research.md`. A trivial
   change does not need the full role set.
4. Re-enter campaign truth through the ledger, evidence, and a Change Report
   even when a subagent or an external runner did the work.

## Practice learned from instances

These are operating rules, not a search policy and not a required harness.
Domain science stays in the instance plan and in `tex_docs/`.

- State which decision the run will change (continue, replace, or stop) before
  spending a large grid. If no outcome would change the next step, do not run it.
- Order the work: small diagnostic, then mechanism, then a small screen, then
  a large confirmation. A larger grid is not stronger evidence.
- Persist the scientific object the next stage needs, not only a summary
  metric. On a smoke subset, check that diagnostic columns are non-degenerate
  before accepting a grid.
- A failed arm is a result. Record what the evidence supports, and stop. Do
  not replace it with a successful-looking output.
- Keep answered questions marked answered, so a later session does not
  re-investigate them as if they were open.
- Two rounds with no new valid result are a signal to diagnose, not to add
  tooling. Resolve routine implementation failures autonomously. Escalate an
  ambiguous scientific choice, an irreversible action, or an unresolved
  high-impact conflict.
- Do not edit another concurrent lane's files. Copy a script you need to change.
- Update on-disk state when the stage changes. A stale in-session checklist
  misleads the next session.
- **Keep this session alive until every assigned task is finished.** Do not
  end it, and do not hand the remaining work to another session, while any
  assigned task remains. A pending or running job is unfinished work in this
  same session: persist the job id, the command, provenance, the output path,
  and the success criterion, keep doing the next piece that does not need
  that result, and continue when the job returns
  (`skills/compute-hosts.md`, `skills/long_running_research_protocol.md`).

## Before any loop

1. Comprehension pass (`skills/project-comprehension.md`).
2. Ledger next unfinished task (`skills/task-ledger.md`).
3. Choose channel: **micro-loop** vs **campaign** (see `experiment-loop.md`).
   Wrong channel is an anti-pattern — not a reason to forbid a better agent.

## Re-entry rules (after the agent runs)

Whatever agent ran — including future ones with unknown features — close the
loop into the OS:

1. Update `TASK_LEDGER.yaml` (state, evidence, settings) — never leave winners
   only inside an agent transcript or a private session dir. Append a row to
   the campaign experiment registry when the loop is a real search
   (`skills/long_running_research_protocol.md`). The session keeps the frontier
   and the next hypothesis, not the full history.
2. Write a Change Report with `plan_ref`.
3. Promote durable hypotheses / results / failures to objects when real.
4. Refresh `COMPREHENSION.md` if plan-vs-code or inventory changed.
5. Prefer portable artefacts (no absolute machine paths; no hard runtime deps on
   private external research repos).

## Evolution rule (keep the template from going stale)

When updating this skill or `experiment-loop.md`:

- **Do** add optional adapters, examples, and clearer re-entry checklists.
- **Do not** encode one agent's current quirks (fixed prompt files, forced
  never-stop UX, required extension APIs, mandatory `.auto/` layout) as the only
  legal path.
- **Do not** break Layer-4 freedom to "make the OS look more automated."
- If a convention becomes obsolete, **deprecate** it; do not force new agents to
  emulate an old harness.

## Data and external assets

Follow the **instance** data skill / lifecycle docs. The OS template does not
hardcode domain QC rules. Agents may search/download when the instance plan says
so — record provenance in the data sibling.

## Anti-patterns

- Treating an agent session log as the project ledger.
- Forcing a multi-day batch campaign into a micro-loop (or the reverse).
- Requiring any one product (e.g. a named IDE extension) for the instance to work.
- Marking ledger tasks `done` from smoke/toy micro-runs.
- Asking the user for permission to continue when the next ledger task is clear
  and unblocked (`project-comprehension.md`).
- **Blocking a stronger agent** because it does not use `.auto/` or
  `tools/experiment.py`.
- Turning OS docs into a frozen prompt library that overrides the agent's own
  capabilities.
