# Requirements — metrics and numerics

You are executing this task. This section is part of the assignment. The
endpoint, the loss scaling, and every published number must be the quantity
the brief named. Do not substitute a nearby metric because it is easier to
compute.

## The endpoint is the brief's quantity

Name the metric, the orientation, the cutoff, and the pairing in the brief.
A signed score and an unsigned score are different. A transpose is not a
sign flip when the target is asymmetric. A cutoff of 1 and a cutoff of 0.1
are different tables. Comparing a corrected series with an uncorrected
historical number is not a result.

If a stored output is in a different orientation from the truth, record the
correction, add a regression test, and recompute. Do not describe the
uncorrected score as "about chance, so the method failed."

## Loss scale

If several terms are added, write the normalisation of each term (per
element, per row, per sample) before the sweep. An unnormalised term changes
the meaning of every coefficient in front of it. A coefficient in one
implementation is not the same penalty as a similarly named coefficient in
another until the formulas are aligned.

## What to check on a smoke run

Shapes, symmetry, finite values, finite gradients, a non-degenerate
diagnostic column, and a paired control that reproduces a known number to
the recorded tolerance. A constant diagnostic column means the column is
broken. Fix it before the grid.

A small-run metric is not evidence about the scientific question
(`writing-a-task-brief.md`).

## Matrix claims

If the output is called a covariance, check that it is one: symmetry,
diagonal, and whether negative eigenvalues are part of the estimator or a
defect. State which. Do not leave a projection implicit.

## Two implementations

Prove equivalence on a shared input before either table is official
(`audit-before-scale.md`). Record where they are allowed to differ.

## Reporting a number

Every decimal in the report must trace to an artefact or to an allow-list
entry that names the measurement. Recompute headline aggregates from the
source files in a script that does not import the analysis code that
produced them (`report-verification.md`).

One unit's result is not a general claim. Say the conditions under which it
holds and the conditions that were not tested.
