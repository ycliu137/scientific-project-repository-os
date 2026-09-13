"""Tests for tools/experiment.py — structured experiment loop."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "experiment.py"


def run_cli(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TOOL), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_init_run_log_keep(tmp_path: Path):
    r = run_cli(
        tmp_path,
        "--dir", ".auto", "init",
        "--name", "demo", "--metric", "mse", "--unit", "1", "--direction", "lower",
    )
    assert r.returncode == 0, r.stderr
    assert (tmp_path / ".auto" / "config.json").is_file()

    r = run_cli(
        tmp_path,
        "--dir", ".auto", "run",
        "--command", "echo METRIC mse=0.5; echo METRIC other=1.0; echo noise",
    )
    assert r.returncode == 0, r.stderr
    assert "METRIC mse=0.5" in r.stdout
    assert "METRIC other=1" in r.stdout
    last = json.loads((tmp_path / ".auto" / "last_run.json").read_text())
    assert last["metrics"] == {"mse": 0.5, "other": 1.0}

    r = run_cli(
        tmp_path,
        "--dir", ".auto", "log", "--status", "keep",
        "--description", "first try", "--asi", "learned=ok",
    )
    assert r.returncode == 0, r.stderr
    record = json.loads((tmp_path / ".auto" / "log.jsonl").read_text().splitlines()[0])
    assert record["run"] == 1 and record["status"] == "keep"
    assert record["metric"] == 0.5
    assert record["asi"] == {"learned": "ok"}


def test_metric_parser_ignores_extra_lines_and_status_best(tmp_path: Path):
    run_cli(tmp_path, "--dir", ".auto", "init", "--name", "d", "--metric", "p")
    run_cli(tmp_path, "--dir", ".auto", "run", "--command", "echo 'METRIC p=0.9'")
    run_cli(tmp_path, "--dir", ".auto", "log", "--status", "keep", "--description", "a")
    run_cli(tmp_path, "--dir", ".auto", "run", "--command", "printf 'not a metric\\nMETRIC p=0.4\\n'")
    run_cli(tmp_path, "--dir", ".auto", "log", "--status", "keep", "--description", "b")

    r = run_cli(tmp_path, "--dir", ".auto", "status")
    assert r.returncode == 0, r.stderr
    assert "best      0.4 (run 2" in r.stdout
    # two runs, delta 0.5 -> improvement 0.5 / floor 0.5 = 1.0
    assert "confidence 1.00x noise floor" in r.stdout


def test_discard_is_recorded_but_best_unchanged(tmp_path: Path):
    run_cli(tmp_path, "--dir", ".auto", "init", "--name", "d", "--metric", "p")
    run_cli(tmp_path, "--dir", ".auto", "run", "--command", "echo METRIC p=0.2")
    run_cli(tmp_path, "--dir", ".auto", "log", "--status", "keep", "--description", "good")
    run_cli(tmp_path, "--dir", ".auto", "run", "--command", "echo METRIC p=0.8")
    run_cli(tmp_path, "--dir", ".auto", "log", "--status", "discard", "--description", "bad")

    r = run_cli(tmp_path, "--dir", ".auto", "status")
    assert "best      0.2 (run 1" in r.stdout
    records = [
        json.loads(line)
        for line in (tmp_path / ".auto" / "log.jsonl").read_text().splitlines()
    ]
    assert [rec["status"] for rec in records] == ["keep", "discard"]


def test_higher_is_better_direction(tmp_path: Path):
    run_cli(
        tmp_path, "--dir", ".auto", "init",
        "--name", "d", "--metric", "r", "--direction", "higher",
    )
    run_cli(tmp_path, "--dir", ".auto", "run", "--command", "echo METRIC r=0.3")
    run_cli(tmp_path, "--dir", ".auto", "log", "--status", "keep", "--description", "a")
    run_cli(tmp_path, "--dir", ".auto", "run", "--command", "echo METRIC r=0.9")
    run_cli(tmp_path, "--dir", ".auto", "log", "--status", "keep", "--description", "b")
    r = run_cli(tmp_path, "--dir", ".auto", "status")
    assert "best      0.9 (run 2" in r.stdout


def test_init_generates_skeleton_files(tmp_path: Path):
    run_cli(tmp_path, "--dir", ".auto", "init", "--name", "d", "--metric", "p")
    for fname in ("prompt.md", "measure.sh", "checks.sh"):
        assert (tmp_path / ".auto" / fname).is_file(), fname
    # the unfilled measure.sh skeleton must fail with a clear TODO message
    r = run_cli(tmp_path, "--dir", ".auto", "run")
    assert r.returncode == 1
    run_log = (tmp_path / ".auto" / "runs" / "run_0001.log").read_text()
    assert "TODO" in run_log


def test_status_without_session_is_clean(tmp_path: Path):
    r = run_cli(tmp_path, "--dir", ".auto", "status")
    assert r.returncode == 0
    assert "no session" in r.stdout
