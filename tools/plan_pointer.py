#!/usr/bin/env python3
"""Print compact live state: ledger, comprehension, NEXT_ACTION; remind consult-plan."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POINTER = ROOT / "workspace" / "current" / "NEXT_ACTION.yaml"
LEDGER = ROOT / "workspace" / "current" / "TASK_LEDGER.yaml"
COMPREHENSION = ROOT / "workspace" / "current" / "COMPREHENSION.md"
PLAN = ROOT / "docs" / "MASTER_PLAN.md"
SKILL = ROOT / "skills" / "consult-plan.md"
LEDGER_SKILL = ROOT / "skills" / "task-ledger.md"
COMPREHENSION_SKILL = ROOT / "skills" / "project-comprehension.md"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sections", action="store_true", help="Print head of MASTER_PLAN.md")
    args = ap.parse_args()

    print(f"consult_plan_skill\t{SKILL.relative_to(ROOT)}\texists={SKILL.is_file()}")
    print(f"task_ledger\t{LEDGER.relative_to(ROOT)}\texists={LEDGER.is_file()}")
    print(f"task_ledger_skill\t{LEDGER_SKILL.relative_to(ROOT)}\texists={LEDGER_SKILL.is_file()}")
    print(
        f"comprehension\t{COMPREHENSION.relative_to(ROOT)}\texists={COMPREHENSION.is_file()}"
    )
    print(
        f"comprehension_skill\t{COMPREHENSION_SKILL.relative_to(ROOT)}\texists={COMPREHENSION_SKILL.is_file()}"
    )
    print(f"next_action_pointer\t{POINTER.relative_to(ROOT)}\texists={POINTER.is_file()}")
    print(f"master_plan\t{PLAN.relative_to(ROOT)}\texists={PLAN.is_file()}")

    if not POINTER.is_file():
        print("ERROR: missing NEXT_ACTION.yaml", file=__import__("sys").stderr)
        return 1

    print("--- TASK_LEDGER.yaml (authoritative task state) ---")
    print(LEDGER.read_text(encoding="utf-8").rstrip() if LEDGER.is_file() else "(missing)")
    if COMPREHENSION.is_file():
        print("--- COMPREHENSION.md (mandatory pre-execution audit) ---")
        print(COMPREHENSION.read_text(encoding="utf-8").rstrip())
    else:
        print("--- COMPREHENSION.md (missing — run skills/project-comprehension.md) ---")
    print("--- NEXT_ACTION.yaml (current-focus pointer) ---")
    print(POINTER.read_text(encoding="utf-8").rstrip())
    print("--- end ---")
    print(
        "NEXT: read skills/task-ledger.md + skills/project-comprehension.md + "
        "skills/consult-plan.md; ledger is authoritative."
    )

    if args.sections and PLAN.is_file():
        print("--- MASTER_PLAN.md (head) ---")
        lines = PLAN.read_text(encoding="utf-8").splitlines()
        print("\n".join(lines[:40]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
