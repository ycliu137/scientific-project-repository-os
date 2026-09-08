# retrieval.md

Prefer the index. Do not walk the tree.

```bash
python3 tools/project_api.py context --task learning
python3 tools/project_api.py inventory
python3 tools/project_api.py list
python3 tools/project_api.py resolve H_000001
python3 tools/nav.py resolve project_api
python3 tools/nav.py resolve next_action
python3 tools/nav.py search experiment
python3 tools/nav.py anywhere <query>
python3 tools/bridge.py status
python3 tools/plan_pointer.py
```

Cold-start: `COLD_START.md`. Learning: `skills/consult-plan.md` (not the whole master plan every time).

## Layers

| Layer | Question | Prefer |
|-------|----------|--------|
| Episodic | What did we run? | `objects/experiments/`, `objects/results/`, `experiments/` |
| Semantic | What do we claim to know? | `objects/claims/` (unproven until linked), hypotheses |
| Procedural | How do we act? | `skills/`, root `SKILL.md` |
| Failure | What went wrong? | `objects/failures/`, `do_not` in NEXT_ACTION |

## Rules

- Hypothesis-driven retrieval > dumping `objects/` or `src/`.
- Run completeness via `context` missing-what, not only filename search.
- After structural adds: `python3 tools/nav.py rebuild`.
- Literature stays `source` / `claim` until an experiment or result links it.
