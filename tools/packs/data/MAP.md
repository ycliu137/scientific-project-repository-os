# MAP.md — Data pack (contract)

Suggested layout (override in this file if the project diverges). Object census is in the pipeline sibling `index/domain_inventory.generated.yaml`. Create dataset folders on first ingest — do not pre-fill empty trees for cosmetics.

| Piece | Path | Contract |
|-------|------|----------|
| Catalog | `catalog.yaml` | Dataset registry |
| Per-dataset | `datasets/<id>/` | Created when registered |
| Template | `datasets/_TEMPLATE/` | Copy for new ids |
| Integrated | `integrated/` | Created when needed |
| Preprocess | `preprocess/` | Scripts that may import source |

`datasets/**/raw/**` is gitignored by default.
