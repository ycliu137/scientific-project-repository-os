# SKILL.md — Paper pack (writing entry)

> **AI operating protocol.** Identity: `os.yaml` → `project.name`.  
> This clone is the **manuscript entry**. Objects live in **pipeline**; the package lives in **source**.

**OS:** Scientific Project Repository OS (paper pack)  
**Siblings:** pipeline (default), source, data — `tools/bridge.py`

You write the paper **here**. You read and test **there**.

```
Paper narrates. Pipeline remembers. Source is the package. Data is the corpus.
No copied src/. No fifth control repo.
```

## Bootstrap

1. This `SKILL.md` → `MAP.md` → `COLD_START.md` (first session)
2. `python3 tools/bridge.py status`
3. `python3 tools/nav.py rebuild` then `python3 tools/plan_pointer.py`
4. `python3 tools/project_api.py context --task write`
5. `skills/paper-entry.md`
6. Code facts: `bridge.py resolve pipeline …` / `bridge.py run source -- pytest -q`
7. Change Report here; integrity on every repo you touched

## Invariants

- Do not duplicate `objects/` here. Cite pipeline IDs.
- Do not `import` siblings as a control package.
- Figures must name `EXP_*` / `R_*` when they come from runs.
- Pipeline `tex_docs/` PDFs are notes, not the submission.
- Manuscript is **English** (`skills/language.md`), even if some pipeline TeX notes are Chinese meeting records.

L2: `consult-plan`, `paper-entry`, `retrieval`, `change-report`.
