# MAP.md — Contract map (not project knowledge)

> Navigation + contracts only. **Census authority** is `index/domain_inventory.generated.yaml`  
> (`python3 tools/project_api.py inventory`). Do not list empty domain “scaffold/live” status here.

This clone’s pack is `os.yaml` → `os.pack`. Source / data / ref / paper are sibling repos (`os.yaml` → `siblings`), not children of this tree.

## How to enter

1. `SKILL.md` (L1)
2. This map (+ `COLD_START.md` on first session)
3. `python3 tools/plan_pointer.py`
4. `python3 tools/project_api.py context --task <intent>` — read **only** listed skills
5. Index: `tools/nav.py` / `project_api`. Siblings: `python3 tools/bridge.py status`

**Default working repo = pipeline.** Open source/data/ref only when the package, corpus, or literature library itself is the task.

## Kernel (ships with the template)

| Piece | Path | Contract |
|-------|------|----------|
| Constitution | `SKILL.md` | L1 entry |
| Instance identity | `os.yaml` | pack + siblings + `include_roots` + `runtime` |
| Procedures | `skills/` | L2 always; L3 via `context` |
| Object type skills | `skills/objects/*.md` | Read when writing that type |
| Object schema | `docs/OBJECT_SCHEMA.md` | Field contract |
| Tools | `tools/` | `nav`, `project_api`, `bridge`, `lab`, `ref_catalog`, `check_project`, `apply_to_repo` |
| Pack overlays | `tools/packs/` | Applied into sibling roots — not a fifth repo |
| Integrity | `tools/check_project.py` | Done-gate |
| Index (committed) | `index/tree.yaml` | Logical tree seed |
| Index (generated) | `index/nav_*.json`, `objects.db`, … | Regenerable |
| Next action | `workspace/current/NEXT_ACTION.yaml` | Live pointer |
| AI design docs | `docs/` | Agents; Change Reports under `docs/change_reports/` |
| TeX notes | `tex_docs/` | Dual-use; Chinese meeting notes OK (`skills/language.md`) |
| Meetings | `meeting_record/` | Private; gitignored |
| Tests | `tests/` | pytest |
| Smoke scripts | `tests/smoke/` | Fast checks (`skills/code-change.md`) |
| Runtimes | `env/` | One `create_*.sh` per env |

## Grown by the instance (create when needed)

Do **not** pre-create these in the template. First write creates the path.

| When | Path | Notes |
|------|------|-------|
| First object of a type | `objects/<domain>/` | Via `project_api create`; skills in `skills/objects/` |
| First pipeline module | `pipelines/<module>/` | README required (`skills/pipeline-modules.md`) |
| Shared path helpers | `pipelines/_shared/` | Path contract builders |
| Run artefacts | `experiments/` | Not Evidence until linked from a result |
| Backend labs | `backend_lab/<lab_id>/` | Disposable sandbox; code in git, `outputs/` ignored; **no external imports**; promote to `tex_docs/` |
| Beamer slides | external `--out` dir | Templates + CLI in pipeline; **no** permanent `slides/` tree (`skills/slides.md`) |
| Scratch drafts | `workspace/scratch/` | `mkdir` when needed; not indexed; gitignored |

Object census (counts / which domains exist): **inventory only** — never hand-maintain status rows in this file.

## Sibling roles

| Role | Typical dirname | Authority |
|------|-----------------|-----------|
| source | `{name}/` | Publicable package |
| pipeline | `{name}_pipeline/` | Objects, runs, AI docs, TeX notes (this pack) |
| data | `{name}_data/` | Raw + processed datasets |
| ref | `{name}_ref/` | Reference PDFs + metadata + BibTeX |
| paper | `{name}_paper/` | Manuscript (late) |

Parent grouping folder is **not** a git repo. Ref is a literature corpus (ingest from pipeline; cite from paper) — not an orchestration layer.

## Authoritative vs temporary

- **Authoritative objects:** pipeline `objects/` with integrity VALID
- **Authoritative package:** source repo (installable, tested)
- **Authoritative data:** data repo layout (adapt per project)
- **Authoritative literature:** ref repo (`catalog.yaml` + `papers/<Title_Slug>/`)
- **Disposable sandboxes:** `backend_lab/` (may delete anytime after TeX promotion; never imported by maintained code) and `workspace/scratch/`
- **Temporary outputs:** `backend_lab/**/outputs/`

- **Private:** `meeting_record/` (not git)
- **Legacy:** `os.yaml` → `legacy_roots`

## Not built yet (do not fake)

- Semantic embeddings index
- Automatic journal submission
- A universal data lake — `skills/data-management.md` is a default; redesign per project
- Any specific scientific method, dataset, or theorem
