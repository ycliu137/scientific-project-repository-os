#!/usr/bin/env python3
"""Compile pipeline tex_docs/**/*.tex to PDF via latexmk.

CJK sources use XeLaTeX (`-xelatex`); otherwise pdfLaTeX (`-pdf`).
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX_ROOT = ROOT / "tex_docs"
CJK_RE = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")


def _latexmk_flags(tex: Path) -> list[str]:
    try:
        text = tex.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        text = ""
    if CJK_RE.search(text):
        return ["-xelatex"]
    return ["-pdf"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--engine", default="latexmk")
    args = ap.parse_args()
    if shutil.which(args.engine) is None:
        print(f"MISSING\t{args.engine} not on PATH", file=sys.stderr)
        return 2
    if not TEX_ROOT.is_dir():
        print("NO_TEX_DOCS")
        return 0
    tex_files = sorted(TEX_ROOT.rglob("*.tex"))
    if not tex_files:
        print("NO_TEX_FILES")
        return 0
    rc = 0
    for tex in tex_files:
        flags = _latexmk_flags(tex)
        print(f"COMPILE\t{tex.relative_to(ROOT)}\t{' '.join(flags)}", flush=True)
        cmd = [args.engine, *flags, "-interaction=nonstopmode", "-halt-on-error", tex.name]
        r = subprocess.call(cmd, cwd=str(tex.parent))
        if r != 0:
            rc = r
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
