# reindex.md

```bash
python3 tools/project_api.py reindex
python3 tools/project_api.py inventory
python3 tools/nav.py rebuild
python3 tools/check_project.py
```

Rebuilds `objects.db` from YAML under `objects/**` with valid headers, writes `index/domain_inventory.generated.yaml`, rebuilds nav. Does not invent objects. Domains appear when the first object of that type is created.
