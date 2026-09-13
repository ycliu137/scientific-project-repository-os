# AUTORESEARCH — OS host architecture (generic)

Status: template design. Companion skills: `skills/autoresearch.md`,
`skills/experiment-loop.md`, `skills/task-ledger.md`,
`skills/project-comprehension.md`.

## Goal

Give every instance a **shared host** for autonomous research loops that:

1. **Helps** agents stay aligned (authority, ledger, comprehension, re-entry).
2. **Does not limit** what a present or **future** autoresearch agent can do.

Autoresearch will matter more over time. The template must stay a **floor**, not
a **ceiling**.

## Plug-in model

```
                    ┌─────────────────────────────────────┐
                    │  Any autoresearch agent (present or │
                    │  future) — owns strategy & autonomy │
                    └──────────────┬──────────────────────┘
                                   │ optional adapter / none
                                   ▼
┌──────────────────────────────────────────────────────────┐
│ OS host (stable)                                         │
│  plan + TASK_LEDGER + COMPREHENSION                       │
│  optional .auto/ + experiment.py (convenience only)      │
│  objects / Change Reports / sibling repos                │
└──────────────────────────────────────────────────────────┘
```

- Agents **plug in**; they are never a dependency of `check_project` or of
  sibling instantiation.
- A new agent with stronger tools, memory, or loop control should work **without
  waiting for this template to invent matching features** — it only needs to
  respect re-entry into ledger + evidence.

## Components shipped by the OS

| Piece | Role | Mandatory? |
|-------|------|------------|
| `skills/autoresearch.md` | Host contract; forward-compat rules | read when looping |
| `skills/experiment-loop.md` | Suggested `.auto/` micro-loop | **no** |
| `tools/experiment.py` | Optional METRIC CLI | **no** |
| `TASK_LEDGER.yaml` | Campaign truth (toy ≠ done) | **yes** for campaigns |
| `COMPREHENSION.md` | Pre-execution audit | **yes** before execute |
| `NEXT_ACTION.yaml` | Focus pointer only | pointer only |

## What instances add

- Domain experiment plan under `docs/`.
- Domain data/QC/lifecycle docs when needed.
- Pipeline modules, measure scripts, cluster drivers.
- Optional thin adapters for a chosen agent — **never required**, never the
  sole path to "valid" research.

## Forward-compatibility checklist (for OS maintainers)

Before merging an OS change that touches autoresearch:

- [ ] Does it still allow an agent that **ignores** `.auto/` / `experiment.py`?
- [ ] Does it avoid naming one vendor as required?
- [ ] Does it add obligations only on **truth/re-entry**, not on agent UX?
- [ ] If deprecating a harness, is the old path still optional rather than
      deleted under agents' feet without a migration note?

## What this document is not

Not a prompt library. Not a fixed hyperparameter schedule. Not a capability
cap on agents. Not a requirement to install any particular IDE extension.
Agents plug in; the OS stays runnable without them; **newer agents must remain
first-class citizens** even when they outgrow shipped convenience tools.
