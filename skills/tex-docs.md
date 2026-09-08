# tex-docs.md

Pipeline `tex_docs/` holds **method / design / derivation** notes, **durable meeting notes**, and **promoted backend-lab records** (process, parameters, results). Dual-use: TeX for agents, PDF for humans. Later paper material — not the manuscript itself (that lives in the paper sibling).

Chinese is allowed **here** for meeting notes (`skills/language.md`). The rest of the project stays English. Chinese `.tex` needs `xeCJK` (or equivalent) and compiles with XeLaTeX (`compile_tex_docs.py` selects `-xelatex` when it sees CJK).

## Write

- One topic per folder or file: `tex_docs/<topic>/<topic>.tex`
- State the `H_*` / `EXP_*` you are explaining when they exist
- Prefer compileable standalone articles (article class is enough)
- Lab promotions: `python3 tools/lab.py promote <lab_id> --tex tex_docs/labs/<topic>` then edit Results/Conclusion (`skills/backend-lab.md`)

## Compile

```bash
python3 tools/compile_tex_docs.py
```

Requires `latexmk` + a TeX engine. Aux files are gitignored; **commit `.tex` and `.pdf`**.

## Do not

- Replace pipeline `docs/` AI notes with TeX only — `docs/` stays the agent-facing design trail
- Put the journal manuscript here once a paper sibling exists (`skills/paper-entry.md`)
- Write the rest of the project in Chinese because a meeting note is Chinese
- Leave important lab findings only inside `backend_lab/` (`notes.md` or `outputs/`) without a TeX / docs promotion
