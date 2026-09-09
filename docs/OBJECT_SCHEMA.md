# Object schema (scientific pack)

Objects are YAML files with `---` front matter + body. Create via `tools/project_api.py`, not by dropping unmarked files.

## Required front-matter fields

| Field | Rule |
|-------|------|
| `id` | `H_######` / `EXP_######` / `CL_######` / `S_######` / `R_######` / `F_######` |
| `type` | `hypothesis` / `experiment` / `claim` / `source` / `result` / `failure` |
| `status` | type-specific (see `skills/objects/<type>.md`) |
| `parent_path` | `{project.slug}/objects/{folder}` |
| `created_at` / `updated_at` | UTC ISO-8601 with `Z` |
| `provenance` | `human` / `ai` / `assimilated` |
| `title` | short |
| `links` | lists of IDs |

## Epistemology

Hypothesis ≠ experiment ≠ result ≠ claim.

- A **claim** may cite sources; it is not a **result**.
- A **result** must name an experiment (and usually a `run_dir` under the instance’s artefact convention, e.g. `outputs/` or `dat/output_*/`).
- Promoting a claim to “accepted” without `links.results` or `links.experiments` is a completeness issue.
- Failures are kept. Do not delete them to tidy the map.

## Folders

| type | directory | prefix |
|------|-----------|--------|
| hypothesis | `objects/hypotheses/` | `H_` |
| experiment | `objects/experiments/` | `EXP_` |
| claim | `objects/claims/` | `CL_` |
| source | `objects/sources/` | `S_` |
| result | `objects/results/` | `R_` |
| failure | `objects/failures/` | `F_` |
