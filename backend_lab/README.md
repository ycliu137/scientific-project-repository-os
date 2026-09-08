# Backend lab

**Disposable** AI/human probes. Commit code + `LAB.yaml` for short-term repro; **gitignore `outputs/`**.  
Nothing outside this tree may import lab code. Important results → `tex_docs/` (not `notes.md`).

- Skill: `skills/backend-lab.md`
- Tool: `python3 tools/lab.py`

```bash
python3 tools/lab.py init <short_slug>
python3 tools/lab.py repro <lab_id> --exec
python3 tools/lab.py promote <lab_id> --tex tex_docs/labs/<topic>
# then the lab folder may be deleted
```
