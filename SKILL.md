# SKILL.md — L1 Constitution (system entry)

> **AI operating protocol.** Not a human README.  
> Identity of **this clone** is `os.yaml` → `project.name`. This file has **no** domain science.

**OS:** Scientific Project Repository OS (`os.yaml` → `os.version`)  
**Pack:** `os.yaml` → `os.pack` (`source` | `pipeline` | `data` | `paper`)  
**On-demand:** `python3 tools/project_api.py context --task <intent>` then read **only** listed skills.

---

## Identity

You are operating a **repository OS** for a scientific project split into **at most four sibling git repos**. The parent folder is only a local grouping directory — not a fifth repo, not a control plane.

```
Skill governs. Index navigates. Retrieval focuses.
Source is the publicable package. Pipeline runs and thinks.
Data holds raw + processed corpora. Paper narrates late.
Hypothesis proposes. Experiment measures. Result records. Claim stays unproven until linked.
```

| Pack | Repo role | Typical publicity | Default entry? |
|------|-----------|-------------------|----------------|
| `pipeline` | Runs, objects, AI docs, TeX notes, meetings | private | **Yes — most work** |
| `source` | Installable package + tests + human README | public at paper time | No — edit/test from pipeline |
| `data` | Raw/processed datasets + preprocess | private | No — operate from pipeline |
| `paper` | Manuscript / figures | as needed | **Only when writing the paper** |

**Working entry:** open the **pipeline** repo for almost everything (design, implement source, test, run, fetch/arrange data, TeX method notes, meetings). **After a paper sibling exists**, write the article **from the paper repo**; read/run source, pipeline, and data through `tools/bridge.py`. Do not copy trees across repos.

**Import rules**

- Pipeline **may and should** `import` the source package (`pip install -e` the source sibling).
- Source **must not** import pipeline or data (keep the package independently runnable and publishable).
- Data preprocess **may** import source for schemas; **must not** import pipeline.
- Paper **must not** import any sibling as a control package; run tests via the bridge.
- Do not invent a fifth orchestration repo.

---

## Bootstrap (mandatory)

Before any meaningful read/write:

1. Read **this** `SKILL.md`
2. Read `MAP.md` (and `COLD_START.md` on first session)
3. Index: `python3 tools/nav.py` / `python3 tools/project_api.py` — **do not** walk the tree or pre-read all `skills/`
4. Compact state: `python3 tools/plan_pointer.py`
5. Task subgraph: `python3 tools/project_api.py context --task <intent>`
6. Read **only** listed L2/L3 skills (plus `skills/objects/<type>.md` if writing that type)
7. Pack extras: `pipeline` → `skills/pipeline-entry.md` when listed; `paper` → `skills/paper-entry.md`; new meeting file → `skills/meeting-record.md`; data layout → `skills/data-management.md`; new host / missing env → `skills/runtime-env.md`
8. Act → index → dense Change Report → `tools/check_project.py` → **VALID** (or WARN-only if `os.strictness: warn`)

Pipeline: `SKILL → MAP → INDEX → compact state → context → listed skills → REASON → UPDATE`

### Find anything

```bash
python3 tools/nav.py rebuild
python3 tools/nav.py resolve skill
python3 tools/nav.py anywhere experiment
python3 tools/project_api.py inventory
python3 tools/bridge.py status
```

Full drill: `COLD_START.md`.

---

## Invariants

1. **H1** This is not a text dump. Indexed objects have schema + `parent_path` + relations. Objects live in the **pipeline** repo.
2. **H2** Cold start = this SKILL → MAP → index. Never grep the whole tree first.
3. **H3** Type skills under `skills/objects/*.md` inherit this file. Object YAML lives under `objects/` (created on first write); do not put `SKILL.md` next to data files.
4. **H4** Updates are writes through the index (`project_api` or equivalent), not stray files under `objects/`.
5. **H5** Every object `parent_path` starts with `project.slug` from `os.yaml`.
6. **H6** No blind edits; Bootstrap first.
7. **H7** At most four sibling repos. Operate source and data **from pipeline** (paper from the paper repo). No fifth control layer.
8. Hypothesis ≠ experiment ≠ result ≠ claim. A claim is not a result.
9. Preserve negative evidence and failures. Do not delete failing experiments to tidy the tree.
10. Do not bulk-create objects to make empty domains look balanced. Empty scaffold is honest.
11. **Optional leakage rule** (L3 when needed): evaluation must not use labels or splits the method would not have had at decision time.
12. Methods compete: propose → test → keep / probation / retire.
13. **Source independence:** the source repo stays a complete, installable package with tests. Pipeline glue, private meetings, and raw data never land in source.
14. **Meetings are private:** `meeting_record/` is gitignored. Adding `YYYYMMDD_meeting.md` requires `YYYYMMDD_action_items.md` the same session (`skills/meeting-record.md`).
15. **TeX notes** in pipeline `tex_docs/` are dual-use (human PDF + machine TeX) and later paper material — compile PDFs (`skills/tex-docs.md`).
16. **Code-change done-gate** (`skills/code-change.md`): pytest + `tests/smoke/` green in `os.yaml` → `runtime` interpreter; minimal diffs; artefact and log **full paths** encode every run-identifying parameter.
17. **One script per environment** (`skills/runtime-env.md`): `env/create_<name>.sh` builds that runtime in one shot. Multiple scripts are expected (laptop, GPU, HPC, CI). Register them in `env/catalog.yaml`. Source `env/` is the publicable default; pipeline may add extra stacks.
18. **Project language is English** (`skills/language.md`). Skills, objects, code, comments, `docs/`, Change Reports, pipelines, env, and the paper manuscript are English. Chinese is allowed only for **meeting records**: durable notes in `tex_docs/`, private transcripts in `meeting_record/`. Promotions into objects or `NEXT_ACTION.yaml` are English.

---

## Lifecycle router

Always-on L2: `consult-plan`, `retrieval`, `adding-knowledge`, `change-report`, `reindex`, `maintenance`, `code-change`, `language`.

| Intent | `--task` |
|--------|----------|
| Bootstrap / clone | `bootstrap` |
| New machine / create env | `env` |
| What next / learning | `learning` |
| New hypothesis / experiment | `experiment` |
| New / change pipeline module | `pipeline` |
| Literature / sources | `literature` |
| Data find / download / preprocess | `data` |
| Meeting record ingested | `meeting` |
| TeX method note | `tex` |
| Write manuscript | `write` |
| Protocol / OS change | `evolution` |
| Navigate only | `retrieval` |

L3 skills exist **on demand**. Completeness is `context` missing-what.

---

## Write Gate

**Preferred:** `python3 tools/project_api.py create …` for objects. Source-package edits: implement in the **source** sibling (from pipeline via bridge), keep source tests green independently.

**Code/pipeline edits:** follow `skills/code-change.md` (project interpreter, tests+smoke green, scoped diffs, path contract).

**Forbidden as done:** drop YAML under `objects/` without index; skip Change Report; copy source/data into paper; commit `meeting_record/` contents; leave pytest/smoke red; omit run parameters from output/log paths; skip `env/create_*.sh` on a new host when `runtime.env_name` is set; write Chinese outside `tex_docs/` / `meeting_record/`.

---

## Humans vs agents

- Humans: source `README.md` + package API; pipeline TeX PDFs; they need not read `docs/`.
- Agents: **must** Bootstrap; `docs/` is for agents; `tex_docs/` is dual-use.
- Do not install git hooks that block human commits on nav rebuild.
