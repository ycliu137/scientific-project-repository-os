# change-report.md — Dense Change Reports

Contract changes leave a trail. Do not emit one empty YAML per micro-diff.

## When required

Write (or amend today’s **theme** report) if any of:

- Objects / skills / OS contracts change
- Experiment protocol or result paths that claims depend on
- Sibling paper/code handoff that affects what the manuscript may say

**Skip a new file** when the change is only: typo, comment, nav rebuild, integrity re-run, or a follow-up that belongs in an open same-day theme report.

## Density

Every report must answer:

1. **why** — intent / problem
2. **artifacts** — paths to reopen
3. **risks** — what not to trust yet
4. **integrity** — VALID | VALID_WITH_WARN | INVALID | NOT_RUN

Prefer `plan_ref`, `skills_followed`, `supersedes`. Reports are **English** (`skills/language.md`).

Same calendar day + same theme → **one** report, amend in place.

## Anti-patterns

- Summary that only repeats filenames
- `integrity: pending` left forever
