# SKILL.md — Ref pack (reference literature)

> Thin constitution. **Ingest and study from the pipeline sibling.**  
> **Cite from the paper sibling** when writing (`bib/references.bib`).

**Pack:** ref  
Layout: `skills/reference-papers.md`

- `catalog.yaml` — paper ids (git)  
- `papers/<Title_Slug>/meta.yaml` — metadata (git)  
- `pdfs/<Title_Slug>.pdf` — unified PDF store (**gitignored**)  
- `bib/references.bib` — citation export  

PDF basename = article **title slug** (same as folder). One merged file per paper (main + appendix).

Bootstrap: this file → `MAP.md` → `catalog.yaml`. Prefer **pipeline** for learning; **paper** for citing.
