# multi-agent-research.md — independent review for substantial research

Use this for a substantial research task: new science, a large experiment, a
redo, or any change whose correctness is not obvious from a small diff.
Trivial edits stay on the lightweight path (one implementer, the normal
done-gate). The goals are scientific correctness, implementation reliability,
independent verification, and efficient autonomous execution.

This skill states **roles and duties**. It does not require a particular
agent product, extension, or model vendor. An instance binds the roles to
whatever runtime it has. One working binding is Pi with a subagent extension
for delegation and a diagnostics extension for code review, using a stronger
reasoning configuration for decisions, reviews, and final verification, and a
faster configuration for routine implementation. Inspect what is actually
installed. Where a role has no native support, use a maintainable substitute
or document the limitation. Validate delegation, review, correction, and final
verification on a small example before a large research task.

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
- Do not declare the task complete without independent verification.

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
- Run independent pieces in parallel when that is safe. Use isolated
  worktrees when concurrent edits would collide.
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

## Sequence for a substantial task

1. **Plan.** Main agent states acceptance criteria and decomposes the work.
2. **Decision review.** Resolve blocking concerns before implementation.
3. **Execute.** Working agents implement, run, and leave reproducible artefacts.
4. **Independent review.** The three reviewers run in parallel.
5. **Correct.** Main agent consolidates findings and delegates fixes.
6. **Re-review.** Repeat the reviews that the fix touches. Reopen decision
   review if an assumption or the objective changed.
7. **Final verification.** PASS, FAIL, or INCONCLUSIVE against the original
   criteria.
8. **Close.** The main agent declares completion only after PASS.

Repeat correction and review as needed. A fixed number of review passes is
not proof of correctness.

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
- Use the lightweight path for a trivial change and this architecture for
  substantial research.
- Parallelize independent reviews and experiments. Do not create conflicting
  writes or resource fights.
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

A substantial task is complete only when:

- the mandatory requirements are met
- the deliverables exist and can be reproduced
- the mathematical, code, and experimental reviews that apply have passed
- blocking findings are resolved
- final verification returned PASS
- remaining limitations and non-blocking issues are written down

A green test suite is not, by itself, evidence of scientific correctness.
