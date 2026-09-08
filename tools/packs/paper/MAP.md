# MAP.md — Paper pack (contract)

Census of scientific objects: pipeline sibling `index/domain_inventory.generated.yaml`. This map is the manuscript tree.

| Piece | Path | Contract |
|-------|------|----------|
| Constitution | `SKILL.md` | Paper-pack entry |
| Manuscript | `tex/` | Create when writing starts |
| Change reports | `docs/change_reports/` | Manuscript themes |
| Pipeline sibling | `os.yaml` → `siblings.pipeline` | Required once created |
| Source sibling | `os.yaml` → `siblings.source` | Required once created |
| Data sibling | `os.yaml` → `siblings.data` | Optional |
| Ref sibling | `os.yaml` → `siblings.ref` | Optional; citations via `bib/` |

Do not bulk-create objects here. Do not pretend this repo owns experiments.
