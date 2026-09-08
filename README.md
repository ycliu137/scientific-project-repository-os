# Scientific Project Repository OS

Template operating system you instantiate into **sibling git repos** so AI agents can reach, read, and govern a scientific project (constitution, indexed navigation, integrity). The kernel carries **no** project-specific science.

**GitHub description:** Template OS for scientific git repos (SKILL, index, integrity). Four siblings: publicable source package, private pipeline (default agent entry), data, and a late paper repo.

Short name: `repo-os`.

**Language:** English everywhere, except Chinese meeting records in pipeline `tex_docs/` and private `meeting_record/` (`skills/language.md`).

---

## Four siblings (parent folder is not a git repo)

```
~/Proj/my_topic/                 # local grouping only
  my_topic/                      # SOURCE — installable package (public at paper time)
  my_topic_pipeline/             # PIPELINE — default AI entry (private)
  my_topic_data/                 # DATA — corpora + preprocess (private)
  my_topic_paper/                # PAPER — late, writing entry
```

| Repo | You put | Public? | Open this to work? |
|------|---------|---------|-------------------|
| source | Package code, tests, human README | yes, later | only for package-only tasks |
| pipeline | Runs, objects, `docs/` (AI), `tex_docs/` (human+AI), meetings | no | **yes, almost always** |
| data | `datasets/`, `integrated/`, preprocess | no | via pipeline bridge |
| paper | Manuscript | as needed | **yes, when writing the paper** |

Pipeline **imports** the source package. Source stays independently runnable and must not import pipeline or data.

---

## New project (three repos at once)

```bash
python3 tools/apply_to_repo.py --layout siblings \
  --parent ~/Proj/my_topic \
  --name my_topic
cd ~/Proj/my_topic/my_topic_pipeline
python3 tools/nav.py rebuild
python3 tools/check_project.py
python3 tools/bridge.py status
# from pipeline: pip install -e ../my_topic
```

Then implement the package in `../my_topic`, runs in `pipelines/` + `experiments/`, datasets in `../my_topic_data`.

---

## Single-repo overlay (existing tree)

```bash
python3 tools/apply_to_repo.py --target /path/to/existing --name foo --pack pipeline --overlay
```

---

## Paper sibling (late)

From the grouping folder:

```bash
python3 /path/to/scientific-project-repository-os/tools/apply_to_repo.py \
  --target ./my_topic_paper \
  --name my_topic_paper \
  --pack paper \
  --sibling-pipeline ../my_topic_pipeline \
  --sibling-source ../my_topic \
  --sibling-data ../my_topic_data
```

Open **the paper repo** to write. Read/test via `python3 tools/bridge.py status`.

---

## Agent entry

Agents: `SKILL.md` → `MAP.md` → `nav` / `project_api` / `bridge`.  
Humans: source README + `tex_docs/*.pdf`. Pipeline `docs/` is for agents.

---

## Pipeline layout (this pack)

| Path | Role |
|------|------|
| `SKILL.md` | L1 constitution |
| `os.yaml` | pack + sibling paths |
| `docs/` | AI design notes + Change Reports |
| `tex_docs/` | dual-use method/math TeX → PDF |
| `meeting_record/` | private; gitignored |
| `tests/` | pytest; smoke scripts in `tests/smoke/` |
| `env/` | one `create_*.sh` per runtime |
| `tools/` | nav, project_api, bridge, check_project, packs |
| `workspace/current/` | NEXT_ACTION pointer |

Instance-grown (create when needed): `objects/`, `pipelines/`, `experiments/`, `workspace/scratch/`.

Upgrade kernel:

```bash
python3 /path/to/scientific-project-repository-os/tools/apply_to_repo.py --target . --upgrade
```
