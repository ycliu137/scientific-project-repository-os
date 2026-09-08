# paper-entry.md — Write from the paper repo

Use when `os.pack` is `paper`, **or** the task is the manuscript after that sibling exists.

## Rule

**Enter the paper repo to write.** Read source, pipeline objects, data, and reference literature through `tools/bridge.py`. Default sibling is **pipeline** (objects + TeX notes). Source tests: `bridge.py run source -- pytest -q`. Citations: pull from the **ref** sibling (`bib/references.bib`, `skills/reference-papers.md`).

Do not copy `src/`, `objects/`, datasets, or the full `papers/` PDF tree into the paper tree.

## Bootstrap extras

```bash
python3 tools/bridge.py status
python3 tools/bridge.py resolve pipeline next_action
python3 tools/bridge.py run ref -- python3 tools/ref_catalog.py export-bib
python3 tools/nav.py anywhere <query>
```

## What lives where

| Live here (paper) | Stay elsewhere |
|-------------------|----------------|
| Journal TeX / figures / captions | Source package; pipeline objects; `tex_docs/` notes |
| Prose citing `H_*` / `EXP_*` / `R_*` | Authoritative YAML in **pipeline** |
| `\cite{…}` / bibliography inputs | Ref sibling `bib/` + `papers/*/meta.yaml` |
| Change Reports about the manuscript | Method/run reports in pipeline |

Mine `../<name>_pipeline/tex_docs/` as material; do not treat those notes as the submission. Manuscript prose is **English** even if some pipeline TeX notes are Chinese meeting records (`skills/language.md`).

## Forbidden

- Changing algorithms only in a paper copy of a script
- Importing siblings as a control package
- An extra orchestration mega-repo
- Duplicating the reference PDF library inside paper/

## Done

Paper Change Report + if source/pipeline/data/ref changed, integrity on those repos too.
