# SKILL.md — Source pack (publicable package)

> Thin constitution. **Default agent entry is the pipeline sibling.**

**Pack:** source  
**Siblings:** `os.yaml` → `siblings.pipeline` / `siblings.data` / `siblings.ref`

You are the **installable package** that will be published with the paper. Keep tests passing here without pipeline or data.

`env/` holds one-shot `create_*.sh` scripts so a stranger can recreate the runtime (`skills/runtime-env.md` in this repo or the pipeline sibling).

```
pip install -e .
pytest -q
```

Pipeline may `import` this package. This repo **must not** import pipeline or data.

If you landed here by mistake for design/runs/meetings: `cd` to the pipeline sibling (`skills/pipeline-entry.md` there).

Bootstrap: this file → `MAP.md` → `python3 tools/nav.py rebuild` if tools exist. Prefer opening **pipeline** for real work.
