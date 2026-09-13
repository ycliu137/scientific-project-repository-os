#!/usr/bin/env python3
"""Structured experiment loop — see ``skills/experiment-loop.md``.

Repo-native micro-iteration accounting for the OS autoresearch host contract
(``skills/autoresearch.md``). Agent-agnostic: does not require any IDE extension.

Commands:

    init   create ``.auto/`` with a session config
    run    run ``.auto/measure.sh`` (or a command) and parse ``METRIC`` lines
    log    append a result record to ``.auto/log.jsonl`` and report confidence
    status show the session, best run and confidence

All paths resolve under ``--dir`` (default ``.auto``) relative to the current
working directory.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

METRIC_RE = re.compile(r"^\s*METRIC\s+([A-Za-z0-9_.\-]+)\s*=\s*(\S+)\s*$")
STATUSES = ("keep", "discard", "crash", "checks_failed")
DIRECTIONS = ("lower", "higher")
DEFAULT_DIR = ".auto"


# --------------------------------------------------------------------------- #
# session files
# --------------------------------------------------------------------------- #
def session_dir(root: Path, name: str) -> Path:
    d = Path(name)
    return d if d.is_absolute() else (root / d)


def load_json(path: Path, default):
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def read_log(sdir: Path) -> list[dict]:
    path = sdir / "log.jsonl"
    if not path.is_file():
        return []
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def append_log(sdir: Path, record: dict) -> None:
    sdir.mkdir(parents=True, exist_ok=True)
    with (sdir / "log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=False) + "\n")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------- #
# metric parsing / scoring
# --------------------------------------------------------------------------- #
def parse_metrics(text: str) -> dict[str, float]:
    """Parse ``METRIC name=number`` lines; ignore everything else."""
    metrics: dict[str, float] = {}
    for line in text.splitlines():
        m = METRIC_RE.match(line)
        if not m:
            continue
        try:
            metrics[m.group(1)] = float(m.group(2))
        except ValueError:
            continue
    return metrics


def is_better(value: float, best: float, direction: str) -> bool:
    return value < best if direction == "lower" else value > best


def best_record(records: list[dict], metric: str, direction: str):
    # Only "keep" runs compete for best; discard/crash runs are recorded but
    # must not pollute the winner (skills/experiment-loop.md).
    kept = [r for r in records if r.get("status") == "keep" and isinstance(r.get("metric"), (int, float))]
    if not kept:
        # Fallback: no keep yet (fresh session) -> any numeric run.
        kept = [r for r in records if isinstance(r.get("metric"), (int, float))]
    if not kept:
        return None
    key = (lambda r: r["metric"]) if direction == "lower" else (lambda r: -r["metric"])
    return min(kept, key=key)


def noise_floor(records: list[dict]) -> float:
    """Median absolute step between consecutive valid primary metrics."""
    vals = [r["metric"] for r in records if isinstance(r.get("metric"), (int, float))]
    if len(vals) < 2:
        return 0.0
    return float(statistics.median(abs(b - a) for a, b in zip(vals, vals[1:])))


def confidence(records: list[dict], direction: str) -> float:
    """Best improvement as a multiple of the session noise floor."""
    valid = [r for r in records if isinstance(r.get("metric"), (int, float))]
    if len(valid) < 2:
        return 0.0
    first = valid[0]["metric"]
    best = best_record(valid, "metric", direction)["metric"]
    improvement = (first - best) if direction == "lower" else (best - first)
    floor = noise_floor(valid)
    if floor <= 0:
        return float("inf") if improvement > 0 else 0.0
    return improvement / floor


def _fmt(value) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #
def cmd_init(args: argparse.Namespace) -> int:
    sdir = session_dir(Path.cwd(), args.dir)
    sdir.mkdir(parents=True, exist_ok=True)
    (sdir / "runs").mkdir(exist_ok=True)
    config = {
        "name": args.name,
        "metric": args.metric,
        "unit": args.unit,
        "direction": args.direction,
        "maxIterations": args.max_iterations,
        "created_at": now_iso(),
    }
    if args.command:
        config["command"] = args.command
    write_json(sdir / "config.json", config)
    for fname in ("log.jsonl", "ideas.md"):
        (sdir / fname).touch()

    # Skeleton session files (fill in the TODOs; do not run with placeholders).
    (sdir / "prompt.md").write_text(
        "# TODO: objective, primary metric, scope, off-limits, constraints, "
        "What's Been Tried\n\n"
        f"metric: {args.metric} ({args.direction} is better)\n"
        "resource caps: <mem/disk/cpu>\n",
        encoding="utf-8",
    )
    (sdir / "measure.sh").write_text(
        "#!/usr/bin/env bash\n"
        "# TODO: run one benchmark and emit exactly: METRIC <name>=<number>\n"
        "set -euo pipefail\n"
        f"echo 'TODO: fill in .auto/measure.sh to emit: METRIC {args.metric}=<number>' >&2\n"
        "exit 1\n",
        encoding="utf-8",
    )
    (sdir / "checks.sh").write_text(
        "#!/usr/bin/env bash\n"
        "# TODO: correctness backpressure (pytest / smoke). Exit non-zero on failure.\n"
        "set -euo pipefail\n"
        "# example: python -m pytest -q\n",
        encoding="utf-8",
    )
    print(f"initialized {sdir}")
    print("next: fill in .auto/prompt.md, .auto/measure.sh, .auto/checks.sh, then `run`")
    return 0


def _resolve_command(args: argparse.Namespace, config: dict, sdir: Path):
    if args.command:
        return args.command
    if config.get("command"):
        return config["command"]
    script = sdir / "measure.sh"
    if script.is_file():
        return f"bash {shlex.quote(str(script))}"
    return None


def cmd_run(args: argparse.Namespace) -> int:
    sdir = session_dir(Path.cwd(), args.dir)
    config = load_json(sdir / "config.json", {})
    command = _resolve_command(args, config, sdir)
    if not command:
        print("error: no command; pass --command or create .auto/measure.sh", file=sys.stderr)
        return 2

    run_no = len(read_log(sdir)) + 1
    t0 = time.time()
    proc = subprocess.run(
        ["bash", "-lc", command],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        timeout=args.timeout,
    )
    elapsed = time.time() - t0
    combined = (proc.stdout or "") + (proc.stderr or "")

    runs_dir = sdir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    (runs_dir / f"run_{run_no:04d}.log").write_text(combined, encoding="utf-8")

    metrics = parse_metrics(combined)
    payload = {
        "run": run_no,
        "command": command,
        "returncode": proc.returncode,
        "seconds": round(elapsed, 3),
        "metrics": metrics,
        "timestamp": now_iso(),
    }
    write_json(sdir / "last_run.json", payload)

    for name, value in metrics.items():
        print(f"METRIC {name}={_fmt(value)}")
    primary = config.get("metric")
    if primary and primary in metrics:
        print(f"primary {primary}={_fmt(metrics[primary])} in {elapsed:.1f}s (rc={proc.returncode})")
    elif metrics:
        print(f"parsed {len(metrics)} metrics in {elapsed:.1f}s (rc={proc.returncode})")
    else:
        print(f"no METRIC lines parsed (rc={proc.returncode}, {elapsed:.1f}s)", file=sys.stderr)
    return 0 if proc.returncode == 0 else proc.returncode


def cmd_log(args: argparse.Namespace) -> int:
    sdir = session_dir(Path.cwd(), args.dir)
    config = load_json(sdir / "config.json", {})
    records = read_log(sdir)
    last = load_json(sdir / "last_run.json", {})

    metric_name = config.get("metric")
    metric = args.metric_value
    if metric is None:
        metric = (last.get("metrics") or {}).get(metric_name)
    if metric is None:
        print(f"error: no metric value (pass --metric-value or run first)", file=sys.stderr)
        return 2

    direction = config.get("direction", "lower")
    record = {
        "run": len(records) + 1,
        "status": args.status,
        "metric": metric,
        "metrics": last.get("metrics", {}),
        "description": args.description or "",
        "asi": dict(args.asi or []),
        "commit": args.commit,
        "timestamp": now_iso(),
    }
    append_log(sdir, record)
    records.append(record)

    best = best_record(records, metric_name, direction)
    conf = confidence(records, direction)
    print(f"logged run {record['run']} [{args.status}] {metric_name}={_fmt(metric)}")
    if best is not None:
        print(f"best {metric_name}={_fmt(best['metric'])} (run {best['run']})")
        print(f"confidence={conf:.2f}x noise floor")
    print("keep -> commit in-scope diff; discard/crash -> revert it (.auto/ preserved)")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    sdir = session_dir(Path.cwd(), args.dir)
    config = load_json(sdir / "config.json", {})
    records = read_log(sdir)
    if not config and not records:
        print(f"(no session at {sdir})")
        return 0
    metric_name = config.get("metric", "metric")
    direction = config.get("direction", "lower")
    print(f"session   {config.get('name', '?')}  [{sdir}]")
    print(f"metric    {metric_name} ({config.get('unit', '')}, {direction} is better)")
    print(f"runs      {len(records)}")
    best = best_record(records, metric_name, direction)
    if best is not None:
        print(f"best      {_fmt(best['metric'])} (run {best['run']}, {best.get('status')})")
        print(f"confidence {confidence(records, direction):.2f}x noise floor")
    for r in records[-5:]:
        print(
            f"  run {r['run']:>3} {r.get('status', '?'):<13} "
            f"{_fmt(r.get('metric'))}  {r.get('description', '')}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="structured experiment loop")
    ap.add_argument("--dir", default=DEFAULT_DIR, help="session dir (default .auto)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="create a session config")
    p.add_argument("--name", required=True)
    p.add_argument("--metric", required=True)
    p.add_argument("--unit", default="")
    p.add_argument("--direction", choices=DIRECTIONS, default="lower")
    p.add_argument("--max-iterations", type=int, default=None)
    p.add_argument("--command", default=None, help="benchmark command (default .auto/measure.sh)")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("run", help="run the benchmark and parse METRIC lines")
    p.add_argument("--command", default=None)
    p.add_argument("--timeout", type=float, default=None)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("log", help="append a result record")
    p.add_argument("--status", choices=STATUSES, required=True)
    p.add_argument("--description", default="")
    p.add_argument("--metric-value", type=float, default=None)
    p.add_argument("--asi", action="append", default=[], metavar="KEY=VALUE")
    p.add_argument("--commit", default=None)
    p.set_defaults(func=cmd_log)

    p = sub.add_parser("status", help="show session, best run and confidence")
    p.set_defaults(func=cmd_status)
    return ap


def _parse_asi(pairs: list[str]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for item in pairs:
        if "=" not in item:
            raise SystemExit(f"--asi expects KEY=VALUE, got {item!r}")
        k, v = item.split("=", 1)
        out.append((k.strip(), v.strip()))
    return out


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "asi", None):
        args.asi = _parse_asi(args.asi)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
