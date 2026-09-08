# env/ — create runtimes with one script per environment

One **`.sh` script = one named environment**. Run it on a new machine; do not hand-assemble conda/pip by memory. Procedure: `skills/runtime-env.md`.

## Layout

```
env/
  README.md
  catalog.yaml           # names, scripts, which machines
  _TEMPLATE.sh           # copy → create_<name>.sh
  create_<name>.sh       # one-shot create/update
  specs/                 # environment.yml / requirements pinned here
```

## Rules

- **Source repo** `env/` is what you publish (third parties reproduce the package).
- **Pipeline repo** `env/` may add extra scripts (workflow tools, cluster CUDA builds) that the public package does not need.
- Each `create_*.sh` is idempotent enough to re-run (create if missing, update if present).
- Register every `create_*.sh` in `catalog.yaml` and point `os.yaml` → `runtime` at the env that script builds.
- No secrets in git (`env/secrets`, `*.local.sh` are gitignored).
- Agents: after cloning on a new host, run the catalog script that matches this machine **before** pytest (`skills/code-change.md`).
