# Requirements — the report

You are executing this task. This section is part of the assignment. The
report in `tex_docs/<topic>/` is for a reader who has not seen the brief.
A markdown summary does not replace the `.tex` and the compiled `.pdf`.
Rereading the report is not a verification. Run the checks below.

## Write as the stages finish

Theory and design go in before the grid: the question, the roster rationale,
the definitions of each shift, the target, and the derivations a reader
would need to check the loss. After each stage, update the TeX, compile the
PDF, and look at the PDF. Do not save the writing for the end.

Keep four kinds of statement apart: a verified fact, a preliminary
observation, a hypothesis not yet tested, and a question the evidence cannot
answer. A reliable negative result is written as a result. Do not keep
tuning until a positive result appears.

## What the report contains

- Why the task exists, and what does not count as success.
- What was compared, on which units, with which factors held fixed.
- The model, the initialisation, and the settings, in the notation of
  `docs/NOTATION.md`. A code variable is not a definition.
- Which code ran, what was reused, what was changed on purpose, and the
  commit.
- Results paired the way the brief required, plus the baseline and the
  density or prevalence the score should be read against.
- Conditions where the conclusion holds, conditions where it does not, and
  evidence that is still missing.
- Failures, runs that did not reach the planned length, and units excluded
  by a declared rule.

A number from a unit that was used to choose a hyperparameter does not
reappear as the confirmation claim (`roster-and-splits.md`).

## Checks before calling the report done

Run these as executable checks where possible, not as another reading.

1. **Recompute.** Headline numbers are recomputed from the source artefacts
   by a script that does not import the analysis code that published them.
   Compare to a tight tolerance.
2. **Trace literals.** Every decimal in the TeX is either a recomputed value
   or an allow-list entry that names the file that measured it. An orphan
   number fails.
3. **Build.** The TeX compiles. The PDF has no table running off the page.
4. **Column provenance.** Each reported column names the metric key it came
   from, including orientation and cutoff.
5. **Scope.** Aggregates include only the declared design. A sibling
   experiment that shares a key must not be folded in by a directory walk.
6. **Determinism.** A second run of the check script reproduces the same
   verdict.

A report that has been reread many times is not thereby correct
(`skills/multi-agent-research.md`). Record the defects the checks found,
including defects that changed a digit without changing the conclusion.

## A redo

Leave the previous report in `tex_docs/`. The new report may cite it as
history. It does not silently reuse the old numbers unless this verification
recomputed them.
