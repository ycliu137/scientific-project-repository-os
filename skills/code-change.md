# code-change.md — Done-gate for every code or pipeline edit

A task that modifies source, pipelines, preprocess, or tests is **not done** until this skill is satisfied. Domain names (conda env, Snakemake, a particular stage folder) belong in the **instance**, not here.

Also: Change Report + `tools/check_project.py`. This skill is the **engineering** half of Done.

---

## 1. Tests green in the project interpreter

After adding or changing code or pipelines:

1. Run **pytest** for touched modules; prefer full `tests/` in that repo when practical.
2. Run **smoke** scripts under `tests/smoke/` when that folder has project scripts (pipeline and/or source).
3. Use the interpreter in `os.yaml` → `runtime` — **`python -m pytest`**, never a stray `pytest` from `~/.local` or another env.
4. If `runtime.env_name` is set, **activate that env first** (`runtime.env_kind`: `micromamba` | `conda` | `venv` | `system`). If the env is missing on this machine, run the matching `env/create_*.sh` from `env/catalog.yaml` (`skills/runtime-env.md`) — do not invent a stray `~/.local` interpreter.
5. Source-package edits: also run tests **in the source cwd** (`tools/bridge.py run source -- python -m pytest -q`).
6. Fix failures and re-run until green. Do not stop on red unless the user **explicitly** accepts a named limitation (record it in the Change Report).

```bash
# example — replace with this instance's runtime.env_name / python
# micromamba activate <env_name>
python -m pytest tests/ -q
# optional smoke scripts
# python tests/smoke/run_all.py
```

---

## 2. Minimal, scoped diffs

Change only what the task requires. Comments, identifiers, and log/artefact **path tokens** are English (`skills/language.md`).

- Do not alter behavior, APIs, or control flow in **unrelated** modules.
- Do not “while we’re here” rewrite other pipelines.
- Shared helpers (`pipelines/_shared/`) may change only when the task needs a shared contract.
- New or renamed **scientific quantities** keep one code name; update pipeline `docs/NOTATION.md` in the same change (`skills/notation.md`).

---

## 3. Artefact and log paths encode the run

Every pipeline output file and every workflow **log** (Snakemake `log:`, Nextflow, shell redirects, etc.) must include **every parameter that distinguishes that run** somewhere in the **full path** (directory segments + filename).

Wildcards and config knobs that identify a run (case/split, seed, model, track, hyperparameters, …) must not be omitted from the path or live only in a sidecar that is easy to lose.

If a single filename would exceed practical limits (e.g. Linux `NAME_MAX`):

- **Split into layered folders**, and/or
- use a **short leaf basename** (`run.log`, `metrics.csv`)

The **complete** set of distinguishing tokens must still appear in the full path.

**Logs** should **mirror** the artefact directory layout (`log/<kind>/…` with the same parent segments as the output). Do not flatten every parameter into one huge log basename.

Prefer **shared path builders** in `pipelines/_shared/` (or equivalent). When you introduce a new layout, add a **path-contract test** (tokens present, length bounds) under `tests/`.

Document the path pattern in the module README heading **Path contract**.

---

## Anti-patterns

- Declaring done after a failed pytest because “it is unrelated”
- Using a different Python than `runtime`
- Skipping `env/create_*.sh` and hand-assembling pip on a new machine
- Seeds/models only in the job name on an HPC scheduler, not in the file path
- Copy-pasting path strings in every rule instead of a shared builder
- Introducing a second identifier for a quantity already named in `docs/NOTATION.md`
