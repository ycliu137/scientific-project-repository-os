# runtime-env.md — One script per environment, many machines

`env/` holds **how to build** the Python (or conda) runtimes. `os.yaml` → `runtime` names **which** env this clone uses for pytest/smoke.

## Where the folder lives

| Repo | `env/` is for |
|------|----------------|
| **source** | Publicable: a stranger clones the package and runs `create_*.sh` |
| **pipeline** | Extra stacks (workflow managers, cluster CUDA) not in the public package |
| data / paper | Usually none; they use source or pipeline env via the bridge |

Prefer putting the **default scientific runtime** in **source** so publication stays reproducible. Pipeline scripts may `source` or call `../<source>/env/create_*.sh` plus extra `env/create_*_pipeline.sh`.

## One script = one env

```bash
cp env/_TEMPLATE.sh env/create_<name>.sh
# edit NAME, KIND, SPEC
chmod +x env/create_<name>.sh
./env/create_<name>.sh
```

Add a row to `env/catalog.yaml` (`name`, `script`, `kind`, `runtime_name`, `hosts`).

Several scripts are expected: laptop CPU, GPU workstation, HPC module stack, CI. Pick the row whose `hosts` matches this machine; do not invent a fourth ad-hoc env in `~/.local`.

## After create

Set this repo’s `os.yaml`:

```yaml
runtime:
  env_kind: micromamba    # must match the script
  env_name: <runtime_name from catalog>
  python: python3
  pytest_module: true
```

Then `skills/code-change.md`: activate that env, `python -m pytest`.

## Agent duties on a new host

1. Read `env/catalog.yaml` (this repo and, from pipeline, the source sibling).
2. Run the matching `create_*.sh` if the env is missing.
3. Do not silently use system Python when `runtime.env_name` is set.

## Do not

- Commit `env/secrets` or `*.local.sh`
- Create envs only in a chat log (“run these pip install lines”)
- One mega-script that asks 20 interactive questions — flags/env vars only
