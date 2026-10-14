# Requirements — roster and splits

You are executing this task. This section is part of the assignment. The
roster is a design, written down before the jobs, not the set of jobs that
happened to finish.

## Do not build the full Cartesian product by default

Vary the factors the questions need. Hold the others at a stated reference
level. A full product of datasets, cell types, networks, models, seeds,
sizes, and depths is an accident of enumeration, not a design. If the grid
starts to explode, that is a stop for the owner, not a reason to submit it.

Cover a factor by a dedicated slice (one-factor-at-a-time around a reference
cell, plus a small core factorial). Say which slice answers which question.

## Matched siblings

When the question is the effect of one factor (depth, noise, a loss), the
siblings share every other latent input. Check that they do: same latent
truth, different observation. A comparison across unrelated draws is a
different question.

## Splits

Name the split unit before training. A unit that leaks across train and
confirmation (the same latent leaf at two depths, split independently) does
not test generalisation.

Keep three roles separate:

| Role | Rule |
|------|------|
| Training | The only data the estimator may fit |
| Development | Used to choose a hyperparameter or a feature set. Those units do not reappear as the confirmation claim |
| Locked confirmation | Untouched until the estimator and the selection rule are frozen. One shot |

## OOD axes stay separate

Report each shift on its own: unseen seed, unseen structure, unseen dataset,
unseen subtype, unseen size, interpolation and extrapolation of a continuous
factor, and a compound shift. A pooled score hides which axis failed.

A production feature must be computable from the observation. A simulator
knob, a ground-truth parameter, or the factor under test is an oracle. Keep
an oracle lane only as a diagnostic, and never in the deployed input.

## When the generator cannot build a cell

Record the structural reason (a model undefined on that graph, a degenerate
covariate at an extreme setting). Do not retry a deterministic failure under
the same seed and call the gap random. Either change the design explicitly
or mark the cell as unbuildable. Coverage is the fraction of the **designed**
roster that exists, after those exclusions are written down.

## Controls

Keep the control the new arm is compared against, including a control that
matches an older, narrower target. Do not delete it when the new target is
adopted. The comparison is the result.
