# Requirements — the task brief

You are executing this task. This section is part of the assignment. The
brief is the design record. Revise it in place in this task folder. Git
history keeps the earlier wording. A redo stays in the same folder and
writes a new report under `tex_docs/`. The same guidance is also in
`skills/auto-tasks.md`. That file stays. Follow this copy without looking
it up.

## What the brief must fix before any large run

Write these before seeing results. A criterion added after the result is a
rationalisation.

1. **Questions, in the order they must be answered.** Each question names the
   decision its outcome would change: continue, replace, or stop. If no
   outcome would change the next step, do not run that experiment.
2. **What is not a result.** A job that exits 0, a lower training loss, or a
   quantity closer to an intermediate target is not success unless the brief
   says that quantity is the endpoint.
3. **Frozen choices.** Inputs, objective, estimator, split, and metric. Say
   which knobs a working agent may tune and which require the owner.
4. **Acceptance, per question.** The comparison, the unit of pairing, the
   sample that counts, and the rule that separates a descriptive observation
   from a confirmatory claim.
5. **Roster shape.** Which factors vary, which stay matched, and why a full
   Cartesian product is or is not required (`roster-and-splits.md`).
6. **Stages.** Each stage has an input, an artefact, and a pass rule. The
   next stage does not start on a failed pass rule.
7. **Where files go.** Task statement in this folder. Progress and handoffs
   in `auto_docs/`. Report in `tex_docs/<topic>/` as `.tex` and `.pdf`.
8. **Stop rules.** Which negative outcomes are results and must be recorded,
   and which changes (objective, generative model, deleting data, cancelling
   a large running set) stop for the owner.
9. **Shared constraints.** Compute placement, device cap, disk budget, and
   what belongs to another concurrent task (`concurrent-sessions.md`).

## Order inside the brief

- The questions and the precondition that would invalidate the whole design
  come first. A historical result that was trained on a degenerate target
  (for example a covariance whose diagonal was forced to 1) is a precondition,
  not a footnote.
- Reuse policy: what may be reused from an earlier campaign, and what must be
  rebuilt because the target or the metric changed.
- Theory and design before the execution stages.
- Execution stages, then the report outline, then session handoff rules.
- Completed history stays in the brief or in `auto_docs/` as a record. It is
  not the specification for the redo.

## Small tests versus the scientific run

A small test checks that the implementation runs: shapes, finite values,
matched controls, a rough wall time. It does not choose a model, a
hyperparameter, or the answer to the brief's questions. Do not mix small-test
numbers into the headline table. Run one small test before a large
submission. Take the scientific conclusion from the scale the brief named.

## After each stage

Save outputs, update the manifest and `auto_docs/` state, update the TeX and
compile the PDF, commit that stage, and continue to the next stage the brief
already authorises. Do not wait until every experiment has finished to start
the report. Do not stop to ask when the brief already names the next step.
