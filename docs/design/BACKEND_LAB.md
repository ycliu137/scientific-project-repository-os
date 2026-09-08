# Design note — Backend lab (disposable probes)

Status: canon in OS v0.5.0 (isolation + dispose-anytime)

## Problem

Agents need short-lived probes. Lab **outputs** must not enter git. Lab **scripts** may be committed for short-term repro, but the project must never **depend** on them. Important findings must live in durable project docs (`tex_docs/`), not inside the lab.

## Decision

`backend_lab/` is a **disposable sandbox**:

| Layer | Content | Git | Longevity |
|-------|---------|-----|-----------|
| Lab code + `LAB.yaml` | recipe / scripts | committed | disposable anytime |
| `notes.md` | scratch | committed | disposable; not canon |
| `outputs/` | artefacts | **ignored** | disposable |
| Durable record | process / params / results | `tex_docs/` etc. | **required** before discard |

**Isolation:** nothing outside `backend_lab/` may import or call lab code. Labs may import the source package.

Tooling: `tools/lab.py`. Skill: `skills/backend-lab.md`.

## Success

Wipe any `backend_lab/<lab_id>/` after promotion: pipelines, source tests, and TeX notes still stand. Repro of a kept recipe is optional convenience, not a dependency.
