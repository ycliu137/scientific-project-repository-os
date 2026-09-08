# TeX method notes (dual-use). See skills/tex-docs.md.

Write `tex_docs/<topic>/<topic>.tex`, then:

```bash
python3 tools/compile_tex_docs.py
```

Commit `.tex` and `.pdf`. Aux files are gitignored. Journal manuscript belongs in the **paper** sibling, not here.

Chinese **meeting notes** are allowed in this folder (`skills/language.md`). Method notes in English are still preferred when they will become paper material.
