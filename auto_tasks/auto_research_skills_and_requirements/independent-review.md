# Requirements — independent review

You are executing this task. This section is part of the assignment. It
applies because the task is substantial. A trivial one-line fix does not
need every role below. A new experiment, a grid, a redo, or a change whose
correctness is not obvious from a small diff does.

The same duties are also in `skills/multi-agent-research.md`. That file
stays. This copy is here so you do not skip review. Roles are duties. Bind
them to whatever subagents this environment actually has. A stronger
reasoning configuration does the plan, the reviews, and the final
acceptance. A faster configuration may do routine implementation. If a role
has no native support, use a separate session that did not write the code,
or write down the substitute. Do not pretend the role was done.

## You do not accept your own implementation

No agent approves work it produced. Reviewers read the original task
statement, the code, the data, and the artefacts. They do not accept a
summary in place of that reading. Keep disagreements. Record which agent
and which model did each stage, and the tool and test outcomes.

## Roles

**Main agent.** Define requirements, assumptions, outputs, and acceptance
criteria before implementation. Decompose the work. Delegate. Resolve
conflicts from evidence, not from a vote. Revisit a decision when new
evidence contradicts it. Do not declare success without the final verifier.

**Decision reviewer.** Before a major implementation stage, and again if a
substantial decision changes, review the plan against the original
requirements. Challenge weak assumptions, missing alternatives, and
unsupported conclusions. Blocking findings are fixed before execution
continues.

**Working agents.** Implement, simulate, submit jobs, test, analyse, and
draft. Follow the approved specification. Do not change a major assumption
or the objective on your own. Parallelise only pieces that do not write the
same files. Report failures. Do not bypass them.

**Three reviewers, in parallel, covering every working agent.**

- Mathematics: assumptions, derivations, dimensions, inverses, transposes,
  normalisation, gradients, objectives, numerical stability. Compare the
  specification with the code. Run an independent numerical test where you
  can. Plausible code is not evidence.
- Code: bugs, edge cases, integration, regressions, and whether the tests
  would catch a wrong implementation. A green suite and clean diagnostics
  are not proof.
- Results and report: configurations, raw outputs, statistics, tables,
  figures. Recompute critical numbers from source data. Check that the
  report matches those outputs and that the conclusion follows. Flag missing
  experiments and unsupported claims. Rereading a report is not a check.

**Final verifier.** Judge the integrated deliverable against the original
acceptance criteria. Do not edit implementation code. Return exactly one of
**PASS**, **FAIL**, or **INCONCLUSIVE**, with evidence. FAIL or
INCONCLUSIVE blocks a claim of success.

**Process verifier.** Watch jobs. Report a stall with the job id, state,
elapsed time, scheduler message, and last progress. A long queue is either
a real backup or a faulty submission (held, bad dependency, unavailable
partition, a reason waiting will not clear). Do not treat a long wait alone
as either verdict. Do not resubmit yourself if you are only the verifier.
Do not change the science while diagnosing a job.

## Sequence

1. Plan, with acceptance criteria.
2. Decision review. Resolve blockers.
3. Execute. Leave reproducible artefacts.
4. The three reviews, in parallel.
5. Correct, then re-review what the fix touches. Reopen decision review if
   an assumption changed.
6. Final verification.
7. Close only on PASS.

Repeat until the blockers are gone. A fixed number of review passes is not
proof.

## Done

Done means the requirements are met, the deliverables reproduce, the
reviews that apply have passed, blockers are resolved, final verification
returned PASS, and the remaining limitations are written down.
