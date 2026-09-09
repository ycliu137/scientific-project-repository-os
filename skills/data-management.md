# data-management.md

Default layout for the **data sibling**. **Redesign if the project needs it** — record the chosen layout in pipeline `docs/` and this repo’s `MAP.md`. Do not pretend one lake fits every field.

## Default tree

```
catalog.yaml                 # index of ids (not the bytes)
datasets/<id>/
  meta.yaml                  # url, paper, license, accessed_at, paths
  raw/                       # original download (often gitignored / LFS)
  processed/                 # pipeline- and source-ready
integrated/<combo_id>/       # merges of multiple datasets
  meta.yaml                  # which <id>s + how
  processed/
preprocess/                  # scripts; may import source; must not import pipeline
```

Copy `datasets/_TEMPLATE/` to `datasets/<id>/` when adding a corpus.

## Agent duties

1. Search/download only what the task needs; write `meta.yaml` **before** treating files as usable.
2. Keep **raw** immutable; write derived files under `processed/` or `integrated/`.
3. Register the id in `catalog.yaml`.
4. Point pipeline runs at **processed** paths, not ad-hoc home folders.
5. Large binaries: gitignore or Git LFS; never commit secrets in URLs with tokens.

## Integrity of provenance

`meta.yaml` should name the source paper/URL. Optionally a pipeline `S_*` object cites the same paper.
