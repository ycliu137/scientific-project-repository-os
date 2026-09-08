# adding-knowledge.md

Objects live in the **pipeline** repo. Create via `project_api` there, not in source/data/paper.

```bash
python3 tools/project_api.py create \
  --type hypothesis \
  --title "..." \
  --body "..." \
  --provenance human
```

Types: `hypothesis` | `experiment` | `claim` | `source` | `result` | `failure`.

API writes YAML under `objects/<type>/`, sets `parent_path`, registers `index/objects.db`, refreshes `index/domain_inventory.generated.yaml`.

Write object titles and bodies in **English** (`skills/language.md`).

Census is `python3 tools/project_api.py inventory` / `index/domain_inventory.generated.yaml`. Do **not** hand-maintain domain status rows in `MAP.md` (MAP is a contract table only).

## When to create

| Type | Create when | Do not |
|------|-------------|--------|
| hypothesis | A falsifiable statement you will test | Vague wishes |
| experiment | A planned or completed run with a protocol | Every debug print |
| claim | An assertion not yet licensed by a result | Copying the paper abstract as fact |
| source | A paper, dataset, or URL used as provenance | A bibliography dump |
| result | A measured outcome linked to an experiment | Scratch plots |
| failure | A test that falsified an H or broke a method | Silence |

## Promote from workspace

1. Draft in `workspace/scratch/` (create the directory if missing; not indexed; gitignored).
2. Validate fields.
3. `create` via API.
4. `link` if needed.
5. Change Report + integrity.

Do not bulk-create empty objects to balance the tree.
