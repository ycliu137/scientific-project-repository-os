# pipeline-modules.md — One README per pipeline module

Pipeline work is split into **modules** under `pipelines/<module>/`. Each module is a thin runner that `import`s the source package. It is **not** a second copy of the package.

## Required layout

```
pipelines/
  README.md                 # catalog + graph of modules (keep current)
  _TEMPLATE/README.md       # copy this when adding a module
  <module>/
    README.md               # required — see headings below
    … scripts …
```

Never add a module directory without `README.md` in the same session. Copy `_TEMPLATE`, then fill it.

## README headings (required)

| Heading | Content |
|---------|---------|
| Purpose | What this module does (one short paragraph) |
| Inputs | Paths, sibling (`data` / `source` / other modules), formats, required columns/files |
| Outputs | Paths under `experiments/` or data `processed/`, formats, what downstream consumes |
| Relations | **Upstream** (must run before) / **Downstream** (consumes this) / **Parallel** (same stage, no order) |
| How to run | Exact command from the pipeline repo root |
| Path contract | How output **and log** full paths encode every run-identifying parameter (`skills/code-change.md`) |

Optional: source-package callables imported; linked `H_*` / `EXP_*`.

## Catalog

When you add, rename, or change edges between modules, update `pipelines/README.md` (table + graph). Integrity warns if a module dir has no README, or README lacks the required headings.

## Do not

- Dump the source package into a module folder
- Leave Inputs/Outputs as “see the code”
- Omit run-identifying parameters from artefact or log paths
- Invent a fifth repo for “just one more pipeline”
