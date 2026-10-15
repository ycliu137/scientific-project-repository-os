#!/usr/bin/env python3
"""Stage completion gate for skills/multi-agent-research.md.

Exit 0 only when the stage directory satisfies the completion predicate.
On success, write gate_result.txt. A hand-written gate_result.txt is not
evidence; this script overwrites it and records hashes of the inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

REVIEW_FILES = (
    "decision_review.md",
    "math_review.md",
    "code_review.md",
    "results_review.md",
)
VERIFIER_FILE = "verifier.md"
REQUIRED_REVIEW_KEYS = (
    "reviewer_role",
    "reviewer_id",
    "main_agent_id",
    "implementer_ids",
    "model",
    "review_round",
    "verdict",
    "inspected",
)
VERDICTS = {"PASS", "FAIL", "INCONCLUSIVE"}
MIN_BODY = 200
SEQUENTIAL_LAUNCH = {
    "",
    "sequential",
    "await",
    "await-each",
    "await_each",
    "serial",
    "one-by-one",
    "for-loop",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def require_concurrent(value: object, label: str, errors: list[str]) -> None:
    text = str(value or "").strip().lower()
    if text in SEQUENTIAL_LAUNCH:
        errors.append(
            f"{label} must name one concurrent launch "
            "(on Pi this is runs.all; sequential await is not accepted)"
        )


def fail(errors: list[str]) -> int:
    for err in errors:
        print(f"FAIL {err}", file=sys.stderr)
    return 1


def parse_header(text: str, path: Path) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    header: dict[str, str] = {}
    for i, line in enumerate(lines):
        if line.strip() == "":
            return header, "\n".join(lines[i + 1 :]).strip()
        if ":" not in line:
            raise ValueError(f"{path.name}: header line has no key: {line!r}")
        key, value = line.split(":", 1)
        header[key.strip()] = value.strip()
    raise ValueError(f"{path.name}: header must end with a blank line before the findings")


def id_set(raw: str) -> set[str]:
    return {part.strip() for part in raw.split(",") if part.strip()}


def parse_time(raw: str, label: str) -> datetime:
    try:
        return datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(f"{label}: timestamp is not ISO-8601: {raw}") from exc


def overlaps(a: dict, b: dict) -> bool:
    a0 = parse_time(a["start"], a["id"])
    a1 = parse_time(a["end"], a["id"])
    b0 = parse_time(b["start"], b["id"])
    b1 = parse_time(b["end"], b["id"])
    if a1 <= a0 or b1 <= b0:
        raise ValueError(f"interval {a['id']} or {b['id']} has end <= start")
    return a0 < b1 and b0 < a1


def any_overlap(intervals: list[dict]) -> bool:
    for i in range(len(intervals)):
        for j in range(i + 1, len(intervals)):
            if overlaps(intervals[i], intervals[j]):
                return True
    return False


def all_overlap(intervals: list[dict]) -> bool:
    if len(intervals) < 2:
        return False
    for i in range(len(intervals)):
        for j in range(i + 1, len(intervals)):
            if not overlaps(intervals[i], intervals[j]):
                return False
    return True


def check_review(path: Path, expected_role: str, errors: list[str]) -> dict[str, str] | None:
    if not path.is_file():
        errors.append(f"missing {path.name}")
        return None
    try:
        header, body = parse_header(path.read_text(encoding="utf-8"), path)
    except ValueError as exc:
        errors.append(str(exc))
        return None
    for key in REQUIRED_REVIEW_KEYS:
        if not header.get(key):
            errors.append(f"{path.name}: missing {key}")
    if header.get("reviewer_role") != expected_role:
        errors.append(f"{path.name}: reviewer_role must be {expected_role}")
    verdict = header.get("verdict", "")
    if verdict not in VERDICTS:
        errors.append(f"{path.name}: verdict must be PASS, FAIL, or INCONCLUSIVE")
    elif verdict != "PASS":
        errors.append(f"{path.name}: verdict is {verdict}, so the stage is not complete")
    reviewer = header.get("reviewer_id", "")
    main = header.get("main_agent_id", "")
    implementers = id_set(header.get("implementer_ids", ""))
    if reviewer and (reviewer == main or reviewer in implementers):
        errors.append(f"{path.name}: reviewer_id matches the main agent or an implementer (self-review)")
    if len(body) < MIN_BODY:
        errors.append(f"{path.name}: findings body is shorter than {MIN_BODY} characters")
    return header


def check_work(stage: Path, errors: list[str]) -> None:
    manifest = stage / "work_manifest.txt"
    if not manifest.is_file():
        errors.append("missing work_manifest.txt")
        return
    root = repo_root()
    lines = [ln.strip() for ln in manifest.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        errors.append("work_manifest.txt is empty")
        return
    for line in lines:
        path = Path(line)
        if not path.is_absolute():
            path = root / path
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"work artifact missing or empty: {line}")


def check_parallelism(stage: Path, errors: list[str]) -> None:
    path = stage / "parallelism.json"
    if not path.is_file():
        errors.append("missing parallelism.json")
        return
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"parallelism.json: {exc}")
        return
    workers = doc.get("workers") or {}
    intervals = workers.get("intervals") or []
    if not isinstance(intervals, list):
        errors.append("parallelism.json: workers.intervals must be a list")
        return
    declared = bool(workers.get("declared_independent"))
    if len(intervals) >= 2 and declared:
        require_concurrent(workers.get("launch"), "independent workers", errors)
        try:
            if not any_overlap(intervals):
                errors.append("declared-independent workers have no overlapping execution interval")
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"worker intervals: {exc}")
    elif len(intervals) >= 2 and not declared:
        if not str(workers.get("serialization_reason") or "").strip():
            errors.append("serialized workers need a non-empty serialization_reason")
    elif declared:
        errors.append("declared_independent requires at least two worker intervals")

    reviews = doc.get("reviews") or {}
    review_intervals = reviews.get("intervals") or []
    ids = {item.get("id") for item in review_intervals if isinstance(item, dict)}
    if ids != {"math", "code", "results"}:
        errors.append("reviews.intervals must be exactly math, code, and results")
        return
    require_concurrent(reviews.get("launch"), "math, code, and results reviews", errors)
    try:
        if not all_overlap(review_intervals):
            errors.append("math, code, and results review intervals do not all overlap")
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"review intervals: {exc}")


def check_deviations(stage: Path, errors: list[str]) -> None:
    path = stage / "protocol_deviations.md"
    if not path.is_file():
        return
    try:
        header, _body = parse_header(path.read_text(encoding="utf-8"), path)
    except ValueError as exc:
        errors.append(str(exc))
        return
    if header.get("unresolved", "").lower() == "true":
        errors.append("protocol_deviations.md is unresolved; a note does not replace the missing role")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_gate(stage: Path, files: list[Path]) -> None:
    lines = ["GATE_OK", f"checked_at: {datetime.now().astimezone().isoformat(timespec='seconds')}"]
    for path in files:
        lines.append(f"{path.name} {sha256(path)}")
    text = "\n".join(lines) + "\n"
    (stage / "gate_result.txt").write_text(text, encoding="utf-8")


def check_stage(stage: Path) -> int:
    errors: list[str] = []
    scope = stage / "scope.json"
    if scope.is_file():
        try:
            doc = json.loads(scope.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return fail([f"scope.json: {exc}"])
        if doc.get("trivial") is True:
            reason = str(doc.get("reason") or "").strip()
            manifest = stage / "work_manifest.txt"
            listed = []
            if manifest.is_file():
                listed = [ln.strip() for ln in manifest.read_text(encoding="utf-8").splitlines() if ln.strip()]
            if not reason:
                errors.append("trivial scope.json needs a non-empty reason")
            if listed:
                errors.append("trivial scope cannot list work artifacts; use the full review gate")
            if errors:
                return fail(errors)
            write_gate(stage, [scope])
            print(f"GATE_OK trivial {stage}")
            return 0

    headers = []
    for name in REVIEW_FILES:
        header = check_review(stage / name, name[: -len("_review.md")], errors)
        if header:
            headers.append(header)
    verifier = check_review(stage / VERIFIER_FILE, "verifier", errors)
    if verifier and headers:
        reviewer_ids = {h.get("reviewer_id", "") for h in headers}
        vid = verifier.get("reviewer_id", "")
        if vid in reviewer_ids:
            errors.append("verifier_id matches one of the four reviewers")
    check_work(stage, errors)
    check_parallelism(stage, errors)
    check_deviations(stage, errors)
    if errors:
        return fail(errors)
    files = [stage / name for name in (*REVIEW_FILES, VERIFIER_FILE, "work_manifest.txt", "parallelism.json")]
    write_gate(stage, files)
    print(f"GATE_OK {stage}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage-dir", type=Path, required=True)
    args = parser.parse_args()
    stage = args.stage_dir
    if not stage.is_absolute():
        stage = repo_root() / stage
    if not stage.is_dir():
        return fail([f"stage directory does not exist: {stage}"])
    return check_stage(stage)


if __name__ == "__main__":
    sys.exit(main())
