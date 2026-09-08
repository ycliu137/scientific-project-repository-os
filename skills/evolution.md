# evolution.md

When changing Protocol / root SKILL / invariants / `os.yaml` pack semantics:

1. Bump `os.version` if the kernel contract changed.
2. Sync packs under `packs/source|data|paper/` if entry rules change.
3. Dense Change Report with `plan_ref`.
4. Do not silently weaken H1–H7 in `SKILL.md`.
5. Keep `workspace/current/NEXT_ACTION.yaml` aligned with `docs/MASTER_PLAN.md`.
6. If the change is a **scientific method** (not the OS): record it as hypothesis/experiment/result, not only as a code comment.

Upgrade an instance from a clean template checkout:

```bash
python3 /path/to/scientific-project-repository-os/tools/apply_to_repo.py \
  --target . --upgrade --name <keep-existing-slug>
```

`--upgrade` overwrites kernel files. It should not clobber `src/`, `objects/`, or (unless you pass flags) `os.yaml` identity — check the script before running on a dirty tree.
