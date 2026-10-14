# Requirements — audit before you scale

You are executing this task. This section is part of the assignment. Do this
before a large roster, a training grid, or treating an existing pipeline as
correct for this task. Write the audit in `auto_docs/`. It is finished when
a later session can reuse the conclusion without re-reading the code.

## Confirm the knob before the roster

If the design depends on a switch (normalisation, depth, a loss term, a
split), run one leaf or one cell and read the artefact.

- The documented switch must actually be plumbed through. A parameter that
  the config accepts and the generator ignores will silently reproduce the
  old experiment.
- The output must be non-degenerate in the direction the design needs. A
  covariance target whose diagonal is constant is a correlation target.
  Training on it does not answer a covariance question.
- If making the knob work requires changing a shared generative model or
  another task's code, stop and align with that owner. Do not patch it from
  inside this task. Copy the script this task needs
  (`concurrent-sessions.md`).

One checked leaf is enough to proceed. An unchecked leaf is not.

## Reuse audit

Before calling an existing evaluator, feature builder, or metric script
correct for the new campaign, write down:

- the CLI flags and the directories they actually read
- the metric's formula, including what is excluded (oracles, other arms,
  other targets)
- hard-coded campaign names, roster paths, and output roots
- whether two experimental arms can collide on the same key and silently
  overwrite each other
- whether a diagnostic column is constant

A script that passes its old tests can still be wrong for the new target.
Clean diagnostics are not proof (`skills/multi-agent-research.md`).

## Equivalence before a number is official

When two implementations are supposed to compute the same quantity, compare
them on a shared input and record the tolerance. Until that check exists,
neither implementation's table is a result.

## Order

1. Audit the observation model, the target, and the existing code.
2. Repair or wrap what the audit rejects.
3. Smoke the repaired path on a handful of units.
4. Only then submit the grid.

A grid that ran on a mis-indexed model, a unit-diagonal target, or a metric
with the wrong orientation is a void result. Record it as void and rerun.
Do not interpret it.
