# MAP.md — Ref pack (contract)

Suggested layout (override here if the project diverges). Object census stays in the **pipeline** sibling.

| Piece | Path | Contract |
|-------|------|----------|
| Constitution | `SKILL.md` | Ref-pack entry |
| Catalog | `catalog.yaml` | Index of ids (git) |
| Paper record | `papers/<Title_Slug>/meta.yaml` | Metadata (git) |
| Notes | `papers/<Title_Slug>/notes.md` | Optional English notes (git) |
| PDFs | `pdfs/<Title_Slug>.pdf` | Unified store; **gitignored**; title-slug name |
| BibTeX | `bib/references.bib` | For paper-pack citing |
| Skill | `skills/reference-papers.md` | Ingest / merge / cite rules |
| Tool | `tools/ref_catalog.py` | list / add / search / validate / merge-pdf / export-bib |

Pipeline sibling: `os.yaml` → `siblings.pipeline` (default study entry).  
Paper sibling: `os.yaml` → `siblings.paper` (citation entry when writing).
