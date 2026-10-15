# multi-agent-research.md — stage gate for substantial research

This is a gate. It is not advice the main agent may simplify.

Use it for a substantial stage: new science, a large experiment, a redo, a
fit, a result table, a scientific report, or any change whose correctness is
not obvious from a small diff. A comment, a typo, or a formatting edit with
no scientific output is the only lightweight path, and only through
`scope.json` as `tools/check_stage_gate.py` defines it.

A substantial stage is **COMPLETE** only when this command exits 0:

```bash
python3 tools/check_stage_gate.py \
  --stage-dir auto_tasks/<task_folder>/auto_docs/reviews/<stage_id>
```

```text
COMPLETE
  iff work artifacts exist
  and decision_review.md, math_review.md, code_review.md, results_review.md exist
  and verifier.md accepts
  and, if workers were declared independent, their execution intervals overlap
```

The checker writes `gate_result.txt` with `GATE_OK` only on that success. A
ledger row or a sentence that says complete without that file is a protocol
failure. The stage is not complete.

The main agent must not waive, merge, or replace a required role. Self-review
is not a review. A green test suite is not a review. Context pressure is not
a review. `protocol_deviations.md` does not fill a missing review file. An
unresolved deviation fails the checker.

Artifacts, one directory per stage, under `auto_docs/reviews/<stage_id>/`:

```text
work_manifest.txt
decision_review.md
math_review.md
code_review.md
results_review.md
verifier.md
parallelism.json
gate_result.txt
protocol_deviations.md
```

`protocol_deviations.md` is written only when a deviation happened. It never
replaces the missing role.

Each review and the verifier start with this header, a blank line, then the
findings:

```text
reviewer_role: decision
reviewer_id: <agent who wrote this file>
main_agent_id: <main agent>
implementer_ids: <comma-separated writers of the stage>
model: <model id>
review_round: 1
verdict: PASS
inspected: <semicolon-separated paths actually opened>
```

`verifier.md` uses `reviewer_role: verifier` and also lists `reviewer_ids:`.
COMPLETE requires `verdict: PASS` on all five files. `reviewer_id` must not
be the main agent or an implementer. The verifier must not be the main agent,
an implementer, or one of the four reviewers. `inspected` must name files
that were opened, not the main agent's summary alone.

`parallelism.json` records ISO-8601 start and end for each worker and for
the math, code, and results reviews. Independent workers, and those three
reviews, are started in one concurrent call. On Pi that call is `runs.all`.
Another runtime writes the name of its own concurrent primitive. The checker
rejects `sequential`, `await`, `await-each`, `serial`, and `one-by-one`.
Endpoint contact is not overlap. The three review intervals must all overlap.
Two or more independent workers need at least one overlapping pair. Serialized
workers need a non-empty `serialization_reason`.

Context length is handled by writing these files and reading the verdict plus
the blocking findings. Cancelling a reviewer to save context is a protocol
deviation and blocks COMPLETE.

Roles below are duties. Bind them to the instance runtime. A missing product
feature is filled by a separate session that did not do the work and still
writes the same file. It is not filled by the main agent reviewing itself.
Prefer a stronger reasoning configuration for the four reviews and the
verifier, and a faster configuration for workers.

Related: `skills/auto-tasks.md`, `skills/autoresearch.md`,
`skills/task-ledger.md`, `skills/compute-hosts.md`.

## Roles

### Main agent — in charge

- Understand the task, plan it, decompose it, decide, coordinate, and integrate.
- Define requirements, mathematical assumptions, expected outputs, and
  measurable acceptance criteria before implementation.
- Delegate implementation to working agents.
- Resolve conflicts from evidence, not from majority agreement.
- Revisit a decision when new evidence contradicts it.
- Do not mark a stage COMPLETE. Only `tools/check_stage_gate.py` exiting 0 does that.

### Decision reviewer — reviews the plan

- Review the main agent's plans, assumptions, mathematical reasoning,
  experimental designs, and major decisions.
- Read the original task statement, not only the main agent's summary.
- Run before major implementation stages and whenever a substantial decision
  changes.
- Challenge weak assumptions, missing alternatives, inconsistencies, and
  unsupported conclusions.
- Report to the main agent. Blocking findings are resolved before execution
  continues.

### Working agents — execute

- Assign as many as the task's independent pieces justify.
- Coding, mathematical implementation, simulation, cluster experiments,
  testing, analysis, and report drafting are all in scope.
- When the pieces are independent, start them in one concurrent call and
  record the intervals in `parallelism.json`. Use isolated worktrees when
  concurrent edits would collide. Sequential await of independent pieces
  is not parallel execution.
- Follow the approved specification. Do not change a major mathematical
  assumption or the experimental objective on their own.
- Produce reproducible outputs, logs, tests, and a clear record of what
  changed.
- Report failures, limitations, and uncertainties. Do not bypass them silently.

### Three reviewers — in parallel, covering every working agent

Split the work by expertise. Together they cover all working-agent outputs.
They inspect original specifications, code, data, and artefacts. They do not
endorse a working agent's explanation in place of that inspection.

**Mathematical correctness.** Check assumptions, derivations, equations,
algorithms, and numerical implementations. Pay particular attention to
inverses, transposes, dimensions, normalization, gradients, objectives, and
numerical stability. Compare the specification with the code. Run independent
numerical tests where possible. Plausible-looking code is not evidence.

**Code correctness and test coverage.** Review the relevant diffs. Look for
bugs, wrong logic, edge cases, integration faults, and regressions. Judge
whether the tests would catch a wrong implementation, not only whether the
current suite is green. Run static analysis, unit tests, integration tests,
and regression tests that fit the change. Clean diagnostics are not proof of
correctness.

**Results and report consistency.** Inspect configurations, execution records,
raw outputs, statistics, tables, figures, and the report. Recompute critical
numbers from source data. Check that tables and figures match those outputs,
and that conclusions follow from the evidence. Flag missing experiments,
inconsistent metrics, misleading comparisons, and unsupported claims. A report
is not correct because it has been reread many times.

### Final verifier — acceptance

- Check the integrated deliverable against the original acceptance criteria,
  not against individual agent reports.
- Run independent acceptance tests and reproduce critical results where that
  is feasible.
- Confirm that blocking findings are resolved.
- Return exactly one of **PASS**, **FAIL**, or **INCONCLUSIVE**, with evidence.
- Do not modify implementation code during final verification.
- FAIL or INCONCLUSIVE blocks the main agent from declaring success.

### Process verifier — runtime and batch-job health

- Watch running processes and submitted jobs throughout execution.
- Detect stalled, failed, hung, or silently idle work. Report each problem
  with a process or job identifier, state, elapsed time, scheduler messages,
  and the last observable progress.
- A long queue wait is a diagnosis, not a verdict. Separate the two cases:
  - resources are occupied, or the queue is genuinely backed up
  - the submission is faulty: never accepted, held, waiting on a dependency
    that will not finish, aimed at an unavailable partition or account, or
    pending for a scheduler reason that waiting will not clear
- A long queue time alone is not a submission failure. A pending state alone
  is not proof that the cluster is full.
- Report a stuck job to the main agent and to the agent that submitted it.
  Resubmission, correction, and cancellation belong to that submitting agent.
- Do not change scientific code, experimental design, or acceptance criteria
  while diagnosing a runtime problem.

## Sequence for a substantial stage

This order is mandatory:

```text
Workers
  → decision review, math review, code review, results review
  → verifier
  → checker exits 0
  → stage COMPLETE
```

1. **Plan.** State acceptance criteria and which workers are independent.
2. **Decision review, before workers.** Another agent reads the original task
   statement. Blocking findings are fixed before implementation. Update the
   same `decision_review.md` if the plan changes.
3. **Workers.** Leave the files named in `work_manifest.txt`.
4. **Math, code, and results reviews, in one concurrent launch.**
5. **Correct.** Send blocking findings back to workers. Workers do not review
   their own fix.
6. **Re-review.** Update the files and increment `review_round`. Reopen
   decision review if an assumption or the objective changed.
7. **Verifier.** Against the original acceptance criteria. Does not edit code.
   Returns exactly `PASS`, `FAIL`, or `INCONCLUSIVE`.
8. **Checker.** Exit 0 writes `gate_result.txt`. Only then is the stage
   COMPLETE.

The process verifier watches jobs during the stage. Its notes are not one of
the four reviews and are not the verifier. A fixed number of review passes
is not proof of correctness. `FAIL` or `INCONCLUSIVE` means the stage is not
complete.

## Independence

- No agent approves its own work.
- Separate implementation, review, and verification.
- Keep reviewer findings, including disagreements.
- Claims of correctness need reproducible evidence.
- Say when evidence is missing, a test was skipped, a tool was unavailable, or
  an experiment is incomplete.
- Do not fabricate results or replace a failed experiment with a
  successful-looking output.
- Do not bypass a failed verification to finish the task.
- When agents disagree, settle it with an independent test.
- Prefer a deterministic executable check over model reasoning alone.
- Record which agent and which model performed each stage, and the important
  tool and test outcomes.

## Efficiency

- Match the number of working agents to how independent the pieces are.
- A trivial edit uses `scope.json` with `{"trivial": true, "reason": "..."}`
  and no work artifacts. Any listed artifact forces the full gate. Uncertainty
  means the full gate.
- Start independent workers together, and start the three reviews together.
  Record the intervals. Do not create conflicting writes.
- Do not repeat an analysis whose evidence is already sufficient.
- Keep a persistent ledger: requirements, decisions, assignments, progress,
  findings, unresolved issues, verification status
  (`skills/task-ledger.md`, `skills/auto-tasks.md`).
- Continue to the next approved task when the previous one is verified.
- Resolve routine implementation problems without stopping for the owner.
- Escalate an ambiguous scientific decision, an irreversible action, or an
  unresolved high-impact conflict. Do not guess.
- Respect compute limits, cluster policy, budgets, and constraints already
  recorded in the instance (`skills/compute-hosts.md`).

## Done

A substantial stage is complete only when `tools/check_stage_gate.py` exits 0
for that stage directory. That exit requires the work artifacts, four PASS
reviews by other agents, a PASS verifier who is none of those agents, and
the parallelism evidence above. Remaining limitations are written in the
verifier body. They do not replace a PASS.

If a required role is skipped, write `protocol_deviations.md` with
`unresolved: true` in the same turn. Set `unresolved: false` only after the
role has been run and its file is present. The checker fails while the
deviation is unresolved.

A green test suite is not, by itself, evidence of scientific correctness.
