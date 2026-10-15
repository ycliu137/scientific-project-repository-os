"""The substantial-stage gate rejects self-review and sequential await."""

import importlib.util
import json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_gate():
    path = ROOT / "tools" / "check_stage_gate.py"
    spec = importlib.util.spec_from_file_location("check_stage_gate", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def header(role, reviewer, **extra):
    fields = {
        "reviewer_role": role,
        "reviewer_id": reviewer,
        "main_agent_id": "main",
        "implementer_ids": "worker-a, worker-b",
        "model": "example-reasoner",
        "review_round": "1",
        "verdict": "PASS",
        "inspected": "SKILL.md",
    }
    fields.update(extra)
    body = "Findings. " + ("Opened the specification and the implementation. " * 12)
    lines = [f"{key}: {value}" for key, value in fields.items()]
    return "\n".join(lines) + "\n\n" + body + "\n"


def intervals(start, minutes, ids):
    t0 = datetime.fromisoformat(start)
    rows = []
    for i, name in enumerate(ids):
        a = t0 + timedelta(minutes=2 * i)
        b = a + timedelta(minutes=minutes)
        rows.append({"id": name, "start": a.isoformat(), "end": b.isoformat()})
    return rows


def write_passing(stage: Path):
    stage.mkdir()
    (stage / "work_manifest.txt").write_text("SKILL.md\n", encoding="utf-8")
    for role, reviewer in (
        ("decision", "rev-d"),
        ("math", "rev-m"),
        ("code", "rev-c"),
        ("results", "rev-r"),
    ):
        (stage / f"{role}_review.md").write_text(header(role, reviewer), encoding="utf-8")
    (stage / "verifier.md").write_text(
        header("verifier", "ver-1", reviewer_ids="rev-d, rev-m, rev-c, rev-r"),
        encoding="utf-8",
    )
    (stage / "parallelism.json").write_text(
        json.dumps(
            {
                "workers": {
                    "declared_independent": True,
                    "launch": "runs.all",
                    "serialization_reason": "",
                    "intervals": intervals("2026-10-15T10:00:00-04:00", 40, ["worker-a", "worker-b"]),
                },
                "reviews": {
                    "launch": "runs.all",
                    "intervals": intervals("2026-10-15T11:00:00-04:00", 30, ["math", "code", "results"]),
                },
            }
        ),
        encoding="utf-8",
    )


def test_passing_stage_writes_gate_ok(tmp_path):
    stage = tmp_path / "ok"
    write_passing(stage)
    assert load_gate().check_stage(stage) == 0
    assert (stage / "gate_result.txt").read_text(encoding="utf-8").startswith("GATE_OK")


def test_self_review_fails(tmp_path):
    stage = tmp_path / "self"
    write_passing(stage)
    text = (stage / "math_review.md").read_text(encoding="utf-8")
    (stage / "math_review.md").write_text(text.replace("reviewer_id: rev-m", "reviewer_id: main"), encoding="utf-8")
    assert load_gate().check_stage(stage) == 1


def test_endpoint_contact_is_not_parallel(tmp_path):
    stage = tmp_path / "seq"
    write_passing(stage)
    doc = json.loads((stage / "parallelism.json").read_text(encoding="utf-8"))
    doc["workers"]["intervals"] = [
        {"id": "worker-a", "start": "2026-10-15T10:00:00-04:00", "end": "2026-10-15T10:20:00-04:00"},
        {"id": "worker-b", "start": "2026-10-15T10:20:00-04:00", "end": "2026-10-15T10:40:00-04:00"},
    ]
    (stage / "parallelism.json").write_text(json.dumps(doc), encoding="utf-8")
    assert load_gate().check_stage(stage) == 1


def test_sequential_launch_name_fails(tmp_path):
    stage = tmp_path / "await"
    write_passing(stage)
    doc = json.loads((stage / "parallelism.json").read_text(encoding="utf-8"))
    doc["reviews"]["launch"] = "await-each"
    (stage / "parallelism.json").write_text(json.dumps(doc), encoding="utf-8")
    assert load_gate().check_stage(stage) == 1


def test_trivial_scope_cannot_hide_work(tmp_path):
    stage = tmp_path / "trivial"
    stage.mkdir()
    (stage / "scope.json").write_text(
        json.dumps({"trivial": True, "reason": "claimed typo"}),
        encoding="utf-8",
    )
    (stage / "work_manifest.txt").write_text("SKILL.md\n", encoding="utf-8")
    assert load_gate().check_stage(stage) == 1
