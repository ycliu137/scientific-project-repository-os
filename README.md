# Scientific Project Repository OS

Template operating system you instantiate into **sibling git repos** so AI agents can reach, read, and govern a scientific project (constitution, indexed navigation, integrity). The kernel carries **no** project-specific science.

**GitHub description:** Template OS for scientific git repos (SKILL, index, integrity). Siblings: publicable source, private pipeline (default agent entry), data, reference literature, and a late paper repo.

Short name: `repo-os`.

**Language:** English everywhere, except Chinese meeting records in pipeline `tex_docs/` and private `meeting_record/` (`skills/language.md`).

---

## Sibling roles (parent folder is not a git repo)

```
~/Proj/my_topic/                 # local grouping only
  my_topic/                      # SOURCE — installable package (public at paper time)
  my_topic_pipeline/             # PIPELINE — default AI entry (private)
  my_topic_data/                 # DATA — corpora + preprocess (private)
  my_topic_ref/                  # REF — reference PDFs + metadata (private)
  my_topic_paper/                # PAPER — late, writing entry
```

| Repo | You put | Public? | Open this to work? |
|------|---------|---------|-------------------|
| source | Package code, tests, human README | yes, later | only for package-only tasks |
| pipeline | Runs, objects, `docs/` (AI), `tex_docs/` (human+AI), meetings | no | **yes, almost always** |
| data | `datasets/`, `integrated/`, preprocess | no | via pipeline bridge |
| ref | `papers/<Title_Slug>/`, `catalog.yaml`, `bib/` | no | ingest via pipeline; cite via paper |
| paper | Manuscript | as needed | **yes, when writing the paper** |

Pipeline **imports** the source package. Source stays independently runnable and must not import pipeline, data, or ref.

**Ref rules:** folder name = article title slug; one merged `paper.pdf` (main + appendix); metadata in `meta.yaml`; study from pipeline; cite from paper (`skills/reference-papers.md`).

---

## New project (source + pipeline + data + ref)

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

Then implement the package in `../my_topic`, runs in `pipelines/` (artefacts under an instance-chosen dir such as `outputs/` or `dat/output_*/`), datasets in `../my_topic_data`, literature in `../my_topic_ref`.

---

## Single-repo overlay (existing tree)

```bash
python3 tools/apply_to_repo.py --target /path/to/existing --name foo --pack pipeline --overlay
```

---

## Ref sibling (literature)

```bash
python3 /path/to/scientific-project-repository-os/tools/apply_to_repo.py \
  --target ./my_topic_ref \
  --name my_topic_ref \
  --pack ref \
  --sibling-pipeline ../my_topic_pipeline \
  --sibling-source ../my_topic \
  --sibling-data ../my_topic_data
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
  --sibling-data ../my_topic_data \
  --sibling-ref ../my_topic_ref
```

Open **the paper repo** to write. Read/test via `python3 tools/bridge.py status`. Export cites: `python3 tools/bridge.py run ref -- python3 tools/ref_catalog.py export-bib`.

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
| `tools/` | nav, project_api, bridge, lab, ref_catalog, **slides**, check_project, packs |
| `workspace/current/` | NEXT_ACTION pointer |
| `backend_lab/` | Disposable probes (code in git for short repro; never imported elsewhere; `outputs/` ignored; promote to `tex_docs/`) |

**Beamer slides** are an **external product** (no permanent `slides/` tree in the pipeline). Templates live under `tools/slides_templates/`; generate into a user `--out` directory:

```bash
python3 tools/slides.py templates
python3 tools/slides.py init --out ~/Slides/MyTalk_YYYYMMDD --template clean_academic \
  --title "…" --author "…"
python3 tools/slides.py compile --dir ~/Slides/MyTalk_YYYYMMDD
```

See `skills/slides.md` (progress talks) and `skills/journal-club-slides.md` (paper decks).

Instance-grown (create when needed): `objects/`, `pipelines/`, `workspace/scratch/`, `backend_lab/<lab_id>/`. Run artefacts are **not** pre-named by the template — pick something obvious (e.g. `outputs/`, `dat/output_*/`) when you need them.

Upgrade kernel:

```bash
python3 /path/to/scientific-project-repository-os/tools/apply_to_repo.py --target . --upgrade
```
