# Requirements — independent review is a gate

You are executing this task. This section is part of the assignment. Follow
it. A substantial stage is not complete because you reviewed it yourself.

The same gate is in `skills/multi-agent-research.md` and
`tools/check_stage_gate.py`. Those files stay. This copy is here so you
run the gate.

A substantial stage is new science, a grid, a redo, a fit, a result table,
a scientific report, or any change whose correctness is not obvious from a
small diff. A comment, a typo, or a formatting edit with no scientific
output is the only case that skips the reviews, and only by writing
`scope.json` with `{"trivial": true, "reason": "..."}` and no work
artifacts. If you are unsure, it is not trivial.

## What COMPLETE means

A stage is COMPLETE only when this command exits 0:

```bash
python3 tools/check_stage_gate.py \
  --stage-dir auto_tasks/<task_folder>/auto_docs/reviews/<stage_id>
```

That exit requires all of the following:

- `work_manifest.txt` lists the specification, the code, and the result
  files, and each path exists and is non-empty.
- `decision_review.md`, `math_review.md`, `code_review.md`, and
  `results_review.md` exist, each with `verdict: PASS`.
- `verifier.md` exists with `verdict: PASS`.
- The author of each review is not you and not an agent who implemented
  the stage. The verifier is not you, not an implementer, and not one of
  the four reviewers.
- If you declared workers independent, `parallelism.json` shows a
  concurrent launch and at least one pair of worker intervals that overlap
  by a positive duration. Touching at an endpoint does not count.
- Math, code, and results reviews were started together. All three
  intervals overlap.

The checker writes `gate_result.txt` with `GATE_OK`. Without that file the
stage is not complete. Do not write `GATE_OK` yourself.

## Order you must follow

```text
Workers
  → decision review, math review, code review, results review
  → verifier
  → checker exits 0
  → stage COMPLETE
```

1. Write the acceptance criteria and which workers are independent.
2. Have another agent write `decision_review.md` from the original task
   statement before workers start. Fix blocking findings first.
3. Workers produce the files in `work_manifest.txt`. They do not review
   their own output.
4. Start the math, code, and results reviewers in one concurrent call.
   On Pi that call is `runs.all([...])`. Another runtime uses its own
   concurrent primitive and records that name in `parallelism.json`.
   Do not await one reviewer and then start the next.
5. Send blocking findings back to workers. Re-review and increment
   `review_round`. Reopen decision review if an assumption changed.
6. A different agent writes `verifier.md` against the original acceptance
   criteria and does not edit code. The verdict is exactly `PASS`,
   `FAIL`, or `INCONCLUSIVE`.
7. Run the checker. Exit 0 is the completion signal.

## Header each review file must have

```text
reviewer_role: decision
reviewer_id: <agent who wrote this file>
main_agent_id: <your id>
implementer_ids: <comma-separated ids>
model: <model id>
review_round: 1
verdict: PASS
inspected: <paths that agent actually opened>
```

Then a blank line and the findings. `inspected` is empty of the files that
were opened only in your summary. The reviewer opens the specification,
the code, and the artifacts.

## What you must not treat as a review

- You, or the worker, writing the review.
- A green test suite, a linter, or clean diagnostics.
- Reading the report again yourself.
- Cancelling a reviewer because the context is long. The reviewer writes
  the file. You read the verdict and the blocking findings.
- `protocol_deviations.md`. Write it in the same turn if a role was
  skipped, with `unresolved: true`. The checker fails while that flag is
  true. Clearing it requires the missing file to exist.

`FAIL` or `INCONCLUSIVE` means the stage is not complete.

## Roles

**Main agent.** Plan, name independent workers, integrate, and send
failures back. You do not write the four reviews or `verifier.md`, and
you do not mark COMPLETE.

**Decision reviewer.** Reads the original requirements before
implementation. Challenges weak assumptions and missing alternatives.

**Workers.** Implement, run, and report failures in the artifacts. They
do not change the objective and do not review themselves.

**Math reviewer.** Checks derivations, dimensions, index conventions,
inverses, transposes, normalisation, gradients, and objectives against
the code. Runs an independent numerical check when one is possible.

**Code reviewer.** Reads the diff for wrong logic and for tests that
would not catch a wrong implementation.

**Results reviewer.** Recomputes the headline numbers from the source
artifacts and checks the report against those numbers.

**Verifier.** Judges the integrated stage against the original
acceptance criteria. Does not edit code.

**Process verifier.** Watches jobs and reports a stall with the job id,
state, elapsed time, and scheduler message. A long queue is either a
real backup or a faulty submission. This role's notes are not a review
file. Do not resubmit if you are only this verifier.
