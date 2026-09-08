# Design note — Reference literature sibling (`ref`)

Status: canon in OS v0.4.0 (+ PDF store policy)  
Generalizes the SPFID `*_ref` practice into the template.

## Problem

Projects need durable **reference PDFs** with structured metadata for learning (from pipeline) and later **citations** (from paper). Dumping PDFs into pipeline `docs/` loses structure; committing thousands of PDFs to GitHub does not scale.

## Decision

Add sibling role `ref` — a literature corpus analogous to `data`, **not** an orchestration/control plane.

| Concern | Rule |
|---------|------|
| Metadata folder | `papers/<Title_Slug>/meta.yaml` (git) |
| PDF store | `pdfs/<Title_Slug>.pdf` — **unified**, **gitignored** |
| Naming | PDF basename = folder = **article title slug** |
| Content | One PDF = main + appendix merged |
| Study entry | **pipeline** via `bridge.py` |
| Cite entry | **paper** via `bib/references.bib` |
| Tooling | `tools/ref_catalog.py` + `skills/reference-papers.md` |

## Meta fields (minimum)

`id`, `title`, `title_slug`, `authors`, `venue`, `published_at`, `kind`, `research_directions`, `problem`, `methods`, `contribution`, `appendix_merged`, `pdf_path`, `cite_key`, `added_at`.

## Anti-patterns

- Pushing `pdfs/*.pdf` to GitHub
- Opaque names (`paper1.pdf`) or PDF name ≠ title slug
- Fifth mega-repo that “controls” the others
- Whole PDF library copied into paper/

## Apply

```bash
python3 tools/apply_to_repo.py --target ./foo_ref --name foo_ref --pack ref \
  --sibling-pipeline ../foo_pipeline --sibling-source ../foo --sibling-data ../foo_data
```

`--layout siblings` also creates `{name}_ref`.
