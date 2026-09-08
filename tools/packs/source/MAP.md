# MAP.md — Source pack (contract)

Package tree (this repo). Scientific object census lives in the **pipeline** sibling (`index/domain_inventory.generated.yaml` there).

| Piece | Path | Contract |
|-------|------|----------|
| Package | `src/<pkg>/` | Create on first module |
| Tests | `tests/` | pytest; optional `tests/smoke/` |
| Runtimes | `env/` | `create_*.sh` + catalog; publicable default |
| Human README | `README.md` | Install / API for humans |
| pyproject | `pyproject.toml` | Installable package |

Do not store pipeline objects, meetings, or raw data here.
