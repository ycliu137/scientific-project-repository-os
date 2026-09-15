# compute-hosts.md — Where agents may run work

Use whenever starting **compute**: training, large sims, sweeps, pytest grids,
autoresearch / PI loops, multi-job Snakemake, or anything heavier than a short
edit/compile. Pair with `skills/runtime-env.md` (which env). Instance projects
override host names / caps in their pipeline `docs/design/` runbook.

## Two-tier model

| Tier | Role |
|------|------|
| **Workstation** | Cursor/edit host: light tests, TeX, interactive smoke |
| **HPC cluster** | **Default for large / parallel / long / multi-GPU / agent auto-experiments** |

Fill instance-specific hostnames, SSH aliases, soft caps, and scheduler
commands in the **pipeline** clone (this template ships the *policy shape*;
sclatcov fills `wanglab-ll1` + SCI/`umass-cluster` in its pipeline skill copy
and `docs/design/CLUSTER_RUNBOOK.md`).

## Decision rule (mandatory)

| Workload | Where |
|----------|--------|
| Tiny: unit test, edit, TeX | Workstation OK |
| **Large / heavy / parallel / agent auto-experiments** | **HPC cluster is the default and first choice** |
| Unsure | **Assume cluster** |

## Workstation soft caps (instance must state numbers)

Document and enforce:

- Max RSS (wrap with a memory watchdog when the host provides one)
- Max concurrent CPU cores for agent-launched jobs
- Disk growth budget for scratch / downloads

Do not assume “all workstation GPUs/RAM are free for agents.”

## Cluster rules (mandatory shape)

1. **Login nodes: zero compute — no exceptions.** Never train, simulate, run
   pytest grids, heavy library work, or leave a Snakemake/parent orchestrator on
   login. Login is for submit/monitor/edit only. Every compute step must run on
   an allocated **compute** node via the batch scheduler.
2. Prefer the site’s **batch scheduler** (LSF / Slurm / … — **check live**, do not guess).
3. Prefer **Snakemake** (or equivalent) + scheduler cluster mode; submit a **driver** so the orchestrator is not stuck on login.
4. **Query resources before large waves** (`bqueues`/`squeue`, host groups, GPU models).
5. **One GPU per job** by default (`exclusive_process` or site equivalent); fan-out across nodes instead of contending on one GPU.
6. When the queue is deep, **leave jobs pending** — do not spill unconstrained work back to the workstation.
7. Pin **GPU generation ↔ CUDA/torch env** when the cluster is heterogeneous.

## Agent checklist

```
- [ ] Large or unsure? → cluster first
- [ ] Workstation caps respected if staying local
- [ ] Login hostname never runs compute
- [ ] Resources checked; GPU pinned; one GPU per job
- [ ] Outputs / .snakemake inside the owning pipeline repo
```

## Anti-patterns

- Treating the edit workstation as the default farm for large jobs
- **Any compute on HPC login nodes** (including “quick” python)
- Leaving the workflow parent on login
- Sharing one GPU across competing jobs
- Ignoring queue backlog and overloading the workstation
- Guessing the wrong scheduler
