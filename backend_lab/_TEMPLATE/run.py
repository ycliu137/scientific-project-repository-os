#!/usr/bin/env python3
"""Ephemeral backend-lab runner template.

Replace with the probe. Keep params in LAB.yaml and encode them in output paths.
"""

from __future__ import annotations

import argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    out = HERE / "outputs" / f"seed{args.seed}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.txt").write_text(f"seed={args.seed}\nok\n", encoding="utf-8")
    print(f"WROTE\t{out / 'result.txt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
