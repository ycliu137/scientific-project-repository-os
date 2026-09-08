#!/usr/bin/env python3
"""Print NEXT_ACTION.yaml and remind consult-plan."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POINTER = ROOT / "workspace" / "current" / "NEXT_ACTION.yaml"
PLAN = ROOT / "docs" / "MASTER_PLAN.md"
SKILL = ROOT / "skills" / "consult-plan.md"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sections", action="store_true", help="Print tail of MASTER_PLAN.md")
    args = ap.parse_args()

    print(f"consult_plan_skill\t{SKILL.relative_to(ROOT)}\texists={SKILL.is_file()}")
    print(f"next_action_pointer\t{POINTER.relative_to(ROOT)}\texists={POINTER.is_file()}")
    print(f"master_plan\t{PLAN.relative_to(ROOT)}\texists={PLAN.is_file()}")

    if not POINTER.is_file():
        print("ERROR: missing NEXT_ACTION.yaml", file=__import__("sys").stderr)
        return 1

    print("--- NEXT_ACTION.yaml ---")
    print(POINTER.read_text(encoding="utf-8").rstrip())
    print("--- end ---")
    print("NEXT: follow skills/consult-plan.md then domain skill; set plan_ref on Change Report.")

    if args.sections and PLAN.is_file():
        print("--- MASTER_PLAN.md (head) ---")
        lines = PLAN.read_text(encoding="utf-8").splitlines()
        print("\n".join(lines[:40]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
