# experiment-loop.md — optional micro-iteration accounting (`.auto/`)

Use when a task is an **optimization micro-loop** *and* you want the
repo-native `.auto/` layout. Parent architecture: `skills/autoresearch.md`
(OS host contract; **agent-agnostic and forward-compatible**).

**This skill is a convenience, not a gate.** A capable autoresearch agent may
use its own session dirs, measure harness, git automation, or stop policy. That
is allowed and preferred when it is stronger — provided campaign truth still
re-enters via `TASK_LEDGER.yaml`, evidence, and a Change Report
(`skills/autoresearch.md` re-entry rules). Do **not** refuse or weaken an agent
because it skips `.auto/` or `tools/experiment.py`.

Tool (optional): `python3 tools/experiment.py`. Related: `skills/code-change.md`,
`skills/change-report.md`, `skills/consult-plan.md`, `skills/task-ledger.md`,
`skills/backend-lab.md`.

## Session files (one `.auto/` per running module or repo root)

| File | Purpose | Committed? |
|------|---------|-----------|
| `.auto/prompt.md` | Playbook: objective, metric, scope, off-limits, constraints, **What's Been Tried** | yes |
| `.auto/measure.sh` | Benchmark; prints `METRIC name=value` lines | yes |
| `.auto/checks.sh` | Correctness backpressure (pytest/smoke); only errors shown | yes |
| `.auto/config.json` | `{name, metric, unit, direction, maxIterations}` | yes |
| `.auto/log.jsonl` | Append-only result log (written by the tool) | yes |
| `.auto/ideas.md` | Idea backlog | yes |
| `.auto/runs/*.log` | Raw benchmark stdout per run | no (gitignored) |
| `.auto/last_run.json` | Last parsed metrics | no (gitignored) |

`.auto/` is **not** a substitute for the OS record: durable outcomes still go to
objects (`experiment` / `result` / `failure`), `tex_docs/`, and a Change Report.

## What this tool is / is NOT (division of labor)

`tools/experiment.py` is a **benchmark runner + append-only micro-ledger**
(parses `METRIC`, appends `log.jsonl`, reports best/confidence). It does **not**
call `git commit`/`revert`, does **not** auto-run `checks.sh`, and does **not**
enforce `maxIterations`.

Full autonomous keep/discard (auto commit/revert, never-stop policy, advanced
tooling) may be provided by an **external** autoresearch agent — including
future agents with features this OS does not model. Those agents are optional,
must still obey the **minimum** host contract in `skills/autoresearch.md`
(ledger / toy≠done / re-entry), and are **not** required to call this CLI or
write `.auto/` files. This CLI is only the repo-native, extension-free
accounting layer for teams that want it.

Three execution channels:

| Channel | Use for | Record of truth |
|---------|---------|-----------------|
| `.auto/` + `experiment.py` (and/or external agent) | **fast micro-iteration** once a measurable unit exists | `.auto/log.jsonl` |
| Pipeline / batch / cluster | **campaigns** (full grids, multi-axis eval) | `TASK_LEDGER.yaml` + artefacts + Change Report |
| OS objects | durable hypotheses / results / failures | `objects/` |

Do **not** force a batch campaign into a "never stop" `.auto/` loop.
Do **not** claim ".auto/ completed Phase X" when campaign results live elsewhere.

## Metric contract

- One **primary** metric (direction `lower` or `higher`). `measure.sh` must emit
  `METRIC <name>=<number>` on stdout; extra `METRIC` lines are secondary.
- Primary improvement → `keep`; worse or equal → `discard`. Secondary metrics
  only break ties.
- Always record **ASI** (free-form `key=value`): what was learned.
- Confidence = `|best - first| / noise_floor` (median absolute step). `>= 2.0`
  likely real; `< 1.0` within noise — re-run before keeping.

## Loop (extension-free)

```bash
python3 tools/experiment.py init --name <goal> --metric <name> --unit <unit> --direction lower
# write .auto/prompt.md and .auto/measure.sh, then:
git checkout -b autoresearch/<goal>-<YYYYMMDD>
python3 tools/experiment.py run
python3 tools/experiment.py log --status keep --description "<idea>" --asi learned="..."
python3 tools/experiment.py status
```

Rules when running the micro-loop (humans or agents):

1. Prefer continuing while the ledger task is open and unblocked; do not ask
   whether to continue on every iteration.
2. Primary metric is king. Simpler code for equal perf = `keep`.
3. `keep` → commit the in-scope diff (agent or human). `discard` / `crash` /
   `checks_failed` → revert the in-scope diff (`.auto/` always preserved).
4. Annotate every run with `asi`. Re-read `.auto/prompt.md` and `.auto/ideas.md`
   on resume.
5. Fix trivial crashes; otherwise log and move on.
6. Keep `.auto/` free of absolute machine paths and of hard runtime deps on
   private external research repos.

## Correctness backpressure

If `.auto/checks.sh` exists, run it after every **passing** benchmark before
`keep`. Green required for `keep`; else log `checks_failed`. Runtime does not
count toward the primary metric (`skills/code-change.md`).

## Resource discipline

Document mem/disk/CPU caps in `.auto/prompt.md`. Cap long runs in `measure.sh`.

## Close-out

Update `.auto/prompt.md` "What's Been Tried", write a Change Report, land the
winner in the normal code/pipeline path, create objects only for real
hypotheses/results/failures. Update `workspace/current/TASK_LEDGER.yaml` if the
loop moved a task. Do not leave the winner only inside `.auto/`.
