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

## Campaign practice

Learned from agent-run campaigns. Instance runbooks fill in the exact scheduler
syntax. This list is the shape.

1. **Pilot, then measure, then size the wave.** Run a small job, record its
   wall time and memory, then set the fan-out and the resource request from
   that measurement. An oversized wall time or memory request is a common
   reason a job stays pending.
2. **Diagnose a long pending job before treating it as either failure or a
   full cluster.** Resources may be occupied or the queue may be backed up.
   Or the submission is faulty: not accepted, held, waiting on a dependency
   that will not finish, aimed at an unavailable partition or account, or
   pending for a scheduler reason that waiting will not clear. A long queue
   time alone is not a submission failure. A pending state alone is not proof
   the cluster is full (`skills/multi-agent-research.md`, process verifier).
3. **When the instance designates a GPU queue for ML, DL, or simulation, use
   it.** Do not relieve a deep GPU queue by falling back to CPU. Leave the job
   pending and diagnose it.
4. **Login nodes are for metadata:** submit, query, list, and transfer. Do not
   analyse large outputs there. Mirror a small result back, or analyse on a
   compute node.
5. **The cluster tree is a separate checkout.** Sync the files the job needs.
   Do not treat cluster git HEAD as provenance of the working tree. Record a
   hash of the code and inputs that actually ran.
6. **Another concurrent lane's files are not yours.** Copy a script you need
   to change. Do not edit it in place.
7. **Idempotency has two checks:** the queue and the artefacts on disk. Either
   check can fail silently (counted the wrong unit, matched no path). Confirm
   both before skipping a submit and before launching a duplicate.
8. **Scheduler success is not scientific success.** Read the exit status, the
   log tail, and the artefact. Record configuration, job id, code revision,
   output path, and the metric. A missing artefact with exit 0 is a failure.
9. **Keep this session alive until every assigned task is finished.** Do not
   end it, and do not hand the remaining work to another session, while any
   assigned task remains. A job in the queue or running is unfinished work
   in this same session. Persist the job id, command, provenance, output
   path, and success criterion so a crash can resume, then keep working:
   prepare whatever does not need this result, and continue the moment the
   job returns (`skills/long_running_research_protocol.md`).

## Agent checklist

```
- [ ] Large or unsure? → cluster first
- [ ] Workstation caps respected if staying local
- [ ] Login hostname never runs compute
- [ ] Resources checked; GPU pinned; one GPU per job
- [ ] Wave sized from a measured pilot, not from an oversized request
- [ ] Pending jobs diagnosed (backed-up queue versus a faulty submission)
- [ ] Outputs / .snakemake inside the owning pipeline repo
```

## Anti-patterns

- Treating the edit workstation as the default farm for large jobs
- **Any compute on HPC login nodes** (including “quick” python)
- Leaving the workflow parent on login
- Sharing one GPU across competing jobs
- Ignoring queue backlog and overloading the workstation
- Guessing the wrong scheduler
- Treating a long pending time as proof the cluster is full, or as proof the submission is broken, without checking which
- Relieving a designated GPU queue by running the same workload on CPU
- Editing another lane's job script instead of copying it
- Ending the session, or handing the work to another session, before every assigned task is finished. A pending or running job is unfinished work in this same session
