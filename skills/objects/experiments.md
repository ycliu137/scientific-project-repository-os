# Type skill — experiments

Read when creating or editing `EXP_*`. The folder `objects/experiments/` is created on the first create (this is the **object registry**, not a bulk dump of run files).

- One protocol, one ID.
- `run_dir`: path to that run’s artefacts. The template does **not** invent a global `experiments/` tree. Prefer a clear instance convention such as `outputs/EXP_######/` or `dat/output_<module>/<run_tag>/`. Create the directory when the run happens.
- Status: `draft` → `planned` → `running` → `done` | `aborted`.
- Link `hypotheses` and, when finished, `results`.
- Parent path: `{slug}/objects/experiments`.
