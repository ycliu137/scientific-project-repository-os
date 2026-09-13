# evolution.md

When changing Protocol / root SKILL / invariants / `os.yaml` pack semantics:

1. Bump `os.version` if the kernel contract changed.
2. Sync packs under `packs/source|data|paper/` if entry rules change.
3. Dense Change Report with `plan_ref`.
4. Do not silently weaken H1–H7 in `SKILL.md`.
5. Keep `workspace/current/NEXT_ACTION.yaml` aligned with the ledger (ledger wins);
   refresh `COMPREHENSION.md` when plan-vs-code changes.
6. Autoresearch changes: update `skills/autoresearch.md` / `experiment-loop.md` only
   for **host contract** or optional convenience — never encode a vendor agent's
   prompts or APIs as the sole legal path. Run the forward-compat checklist in
   `docs/design/AUTORESEARCH.md` before merging. Newer agents must stay first-class.
6. If the change is a **scientific method** (not the OS): record it as hypothesis/experiment/result, not only as a code comment.

Upgrade an instance from a clean template checkout (see
`docs/design/APPLY_AND_UPGRADE.md`):

```bash
python3 /path/to/scientific-project-repository-os/tools/apply_to_repo.py \
  --target . --upgrade --dry-run
python3 /path/to/scientific-project-repository-os/tools/apply_to_repo.py \
  --target . --upgrade
```

`--upgrade` refreshes shipped kernel files **only when the instance did not
modify them** (tracked in `OS_APPLIED.yaml`). Modified files are listed in
`OS_ABSORB.md` for the agent to merge template improvements into the instance
copy. KEEP_ON_UPGRADE (ledger/comprehension/plans) is never overwritten.
`os.yaml` / `.gitignore` are merged. Do not run on a dirty tree without
`--dry-run` first. After absorb merges: `--record-hashes`.
