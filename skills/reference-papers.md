# reference-papers.md — Reference literature sibling

Use when ingesting, organizing, or citing **project reference PDFs**.

**Default session root = pipeline.** Ingest and study papers from pipeline via `tools/bridge.py`.  
**When writing the manuscript**, open the **paper** pack and pull cite keys / BibTeX from the **ref** sibling — do not copy PDF trees into paper.

## Layout (ref pack)

```
catalog.yaml                 # index of paper ids (in git)
papers/
  _TEMPLATE/
    meta.yaml
    notes.md
  <Title_Slug>/
    meta.yaml                # in git
    notes.md                 # optional; in git
pdfs/
  README.md                  # in git
  <Title_Slug>.pdf           # ALL PDFs here; gitignored
bib/
  references.bib             # optional export for the paper sibling
```

**Naming rule (required):**

- Folder: `papers/<Title_Slug>/` — sanitized **article title**
- PDF: `pdfs/<Title_Slug>.pdf` — **same title slug** (main + appendix already merged)

Do not use `paper1.pdf` or author-year-only names.  
Slug helper: `python3 tools/ref_catalog.py slug "Full Title Here"`.

**Git policy:** commit metadata + BibTeX; **gitignore all `pdfs/*.pdf`**. PDFs stay on local disk / lab storage shared with the ref checkout.

## Required `meta.yaml` fields

| Field | Meaning |
|-------|---------|
| `id` | Stable id, e.g. `REF_000001` |
| `title` | Full title |
| `title_slug` | Must match folder name **and** PDF basename |
| `authors` | List of author strings |
| `venue` | Journal / conference / preprint server |
| `published_at` | ISO date or `YYYY-MM` / `YYYY` |
| `kind` | `experiment` \| `algorithm` \| `analysis` \| `review` \| `theory` \| `other` |
| `research_directions` | List of short direction tags |
| `problem` | What problem the paper addresses |
| `methods` | List of methods / techniques used |
| `contribution` | One-paragraph takeaway for *this* project |
| `appendix_merged` | `true` when appendix is merged into the PDF |
| `pdf_path` | Relative path, normally `pdfs/<Title_Slug>.pdf` |
| `doi` / `url` | Identifiers when known |
| `added_at` | UTC date added |
| `tags` | Free tags |
| `cite_key` | BibTeX key for paper writing |
| `pipeline_sources` | Optional list of pipeline `S_*` ids |

## Agent duties

1. From **pipeline**: `python3 tools/bridge.py run ref -- python3 tools/ref_catalog.py …`
2. Before treating a PDF as usable: write `meta.yaml`, register in `catalog.yaml`, place PDF under `pdfs/<Title_Slug>.pdf`.
3. If the publisher ships a separate appendix: **merge** into `pdfs/<Title_Slug>.pdf` (`merge-pdf --slug …`), set `appendix_merged: true`.
4. Reading notes go in `notes.md` (English). Promotions into pipeline objects stay in pipeline.
5. For manuscript citations: `export-bib`; cite from the **paper** repo without committing PDFs.
6. Never commit secrets in download URLs. Do not push thousands of PDFs to GitHub.

## Commands

```bash
# from pipeline
python3 tools/bridge.py run ref -- python3 tools/ref_catalog.py list
python3 tools/bridge.py run ref -- python3 tools/ref_catalog.py search spatial
python3 tools/bridge.py run ref -- python3 tools/ref_catalog.py validate

# inside ref repo
python3 tools/ref_catalog.py add --title "..." --kind algorithm --pdf /path/in.pdf
python3 tools/ref_catalog.py merge-pdf main.pdf si.pdf --slug Some_Paper_Title
python3 tools/ref_catalog.py export-bib
```

## Anti-patterns

- Committing `pdfs/*.pdf` to git
- Opaque names (`paper1.pdf`) or PDF basename ≠ `title_slug`
- Separate long-lived “main.pdf” + “SI.pdf” (merge them)
- Copying the PDF library into pipeline or paper
- Treating ref as a control mega-repo
