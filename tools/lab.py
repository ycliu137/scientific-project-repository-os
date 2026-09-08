#!/usr/bin/env python3
"""Manage ephemeral backend_lab instances.

Examples:
  python3 tools/lab.py init factor_ablation_C
  python3 tools/lab.py list
  python3 tools/lab.py show 20260908_factor_ablation_C
  python3 tools/lab.py repro 20260908_factor_ablation_C
  python3 tools/lab.py repro 20260908_factor_ablation_C --exec
  python3 tools/lab.py promote 20260908_factor_ablation_C --tex tex_docs/labs/factor_ablation_C
  python3 tools/lab.py status 20260908_factor_ablation_C promoted
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = ROOT / "backend_lab"
TEMPLATE = LAB_ROOT / "_TEMPLATE"

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path) -> dict:
    if yaml is None:
        raise SystemExit("PyYAML required (pip install pyyaml)")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must be a mapping")
    return data


def _dump(data: dict) -> str:
    if yaml is None:
        raise SystemExit("PyYAML required (pip install pyyaml)")
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def _slugify(s: str) -> str:
    s = re.sub(r"[^\w\-]+", "_", s.strip(), flags=re.UNICODE)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "lab"


def lab_dir(lab_id: str) -> Path:
    return LAB_ROOT / lab_id


def iter_labs() -> list[Path]:
    if not LAB_ROOT.is_dir():
        return []
    out = []
    for p in sorted(LAB_ROOT.iterdir()):
        if p.is_dir() and not p.name.startswith("_") and (p / "LAB.yaml").is_file():
            out.append(p)
    return out


def cmd_init(args: argparse.Namespace) -> int:
    if not TEMPLATE.is_dir():
        print(f"MISSING_TEMPLATE\t{TEMPLATE}", file=sys.stderr)
        return 2
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    slug = _slugify(args.slug)
    lab_id = args.id or f"{day}_{slug}"
    dest = lab_dir(lab_id)
    if dest.exists() and not args.force:
        print(f"EXISTS\t{dest}", file=sys.stderr)
        return 2
    dest.mkdir(parents=True, exist_ok=True)
    for name in ("LAB.yaml", "run.py", "notes.md"):
        src = TEMPLATE / name
        if src.is_file():
            shutil.copy2(src, dest / name)
    (dest / "outputs").mkdir(exist_ok=True)
    card = _load(dest / "LAB.yaml")
    card["id"] = lab_id
    card["created_at"] = utc_now()
    card["status"] = "active"
    if args.purpose:
        card["purpose"] = args.purpose
    (dest / "LAB.yaml").write_text(_dump(card), encoding="utf-8")
    print(f"INIT\t{dest}")
    print("NEXT\tedit LAB.yaml + run.py; then: python3 tools/lab.py repro", lab_id)
    return 0


def cmd_list(_: argparse.Namespace) -> int:
    labs = iter_labs()
    if not labs:
        print("EMPTY\tbackend_lab/")
        return 0
    for d in labs:
        meta = _load(d / "LAB.yaml")
        print(f"{meta.get('status', '?')}\t{d.name}\t{str(meta.get('purpose', '')).splitlines()[0][:80]}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    d = lab_dir(args.lab_id)
    path = d / "LAB.yaml"
    if not path.is_file():
        print(f"NO_LAB\t{d}", file=sys.stderr)
        return 2
    print(path.read_text(encoding="utf-8"))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    d = lab_dir(args.lab_id)
    path = d / "LAB.yaml"
    if not path.is_file():
        print(f"NO_LAB\t{d}", file=sys.stderr)
        return 2
    card = _load(path)
    card["status"] = args.status
    path.write_text(_dump(card), encoding="utf-8")
    print(f"STATUS\t{args.lab_id}\t{args.status}")
    return 0


def cmd_repro(args: argparse.Namespace) -> int:
    d = lab_dir(args.lab_id)
    path = d / "LAB.yaml"
    if not path.is_file():
        print(f"NO_LAB\t{d}", file=sys.stderr)
        return 2
    card = _load(path)
    cmds = card.get("commands") or []
    cwd_mode = str(card.get("cwd") or "lab")
    cwd = str(d if cwd_mode == "lab" else ROOT)
    py = ((card.get("runtime") or {}) or {}).get("python") or "python3"
    print(f"LAB\t{args.lab_id}\tcwd={cwd}")
    for c in cmds:
        line = str(c)
        if line.startswith("python ") and py != "python":
            line = py + line[len("python") :]
        print(f"CMD\t{line}")
        if args.exec:
            rc = subprocess.call(line, shell=True, cwd=cwd)
            if rc != 0:
                print(f"FAIL\trc={rc}", file=sys.stderr)
                return rc
    if not args.exec:
        print("HINT\tadd --exec to run")
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    d = lab_dir(args.lab_id)
    path = d / "LAB.yaml"
    if not path.is_file():
        print(f"NO_LAB\t{d}", file=sys.stderr)
        return 2
    card = _load(path)
    tex_rel = args.tex.strip().rstrip("/")
    tex_dir = ROOT / tex_rel
    tex_dir.mkdir(parents=True, exist_ok=True)
    topic = tex_dir.name
    tex_path = tex_dir / f"{topic}.tex"
    params = card.get("params") or {}
    param_rows = "\n".join(
        f"  \\item \\texttt{{{k}}}: {v}" for k, v in params.items()
    ) or "  \\item (none recorded)"
    cmds = card.get("commands") or []
    cmd_rows = "\n".join(f"  \\item \\texttt{{{c}}}" for c in cmds) or "  \\item (none)"
    summary = card.get("results_summary") or "TODO: summarize numeric / qualitative results."
    purpose = str(card.get("purpose") or "").strip()
    body = f"""\\documentclass{{article}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{hyperref}}
\\begin{{document}}
\\title{{Lab note: {topic.replace('_', ' ')}}}
\\author{{SPFID pipeline backend\\_lab}}
\\date{{}}
\\maketitle

\\section{{Purpose}}
{purpose}

\\section{{Lab id}}
\\texttt{{{args.lab_id}}} (ephemeral; see \\texttt{{skills/backend-lab.md}})

\\section{{Parameters}}
\\begin{{itemize}}
{param_rows}
\\end{{itemize}}

\\section{{Commands}}
\\begin{{itemize}}
{cmd_rows}
\\end{{itemize}}

\\section{{Results}}
{summary}

\\section{{Conclusion}}
TODO

\\end{{document}}
"""
    if tex_path.exists() and not args.force:
        print(f"EXISTS\t{tex_path}\t(use --force to overwrite)", file=sys.stderr)
        return 2
    tex_path.write_text(body, encoding="utf-8")
    card["promote_to"] = tex_rel
    card["status"] = "promoted"
    path.write_text(_dump(card), encoding="utf-8")
    print(f"PROMOTED\t{tex_path}")
    print("NEXT\tfill Results/Conclusion; python3 tools/compile_tex_docs.py")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init")
    p.add_argument("slug", help="short slug; date prefix added automatically")
    p.add_argument("--id", default=None, help="override full lab_id")
    p.add_argument("--purpose", default="")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    sub.add_parser("list").set_defaults(func=cmd_list)

    p = sub.add_parser("show")
    p.add_argument("lab_id")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("status")
    p.add_argument("lab_id")
    p.add_argument("status", choices=["active", "done", "promoted", "discarded"])
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("repro")
    p.add_argument("lab_id")
    p.add_argument("--exec", action="store_true")
    p.set_defaults(func=cmd_repro)

    p = sub.add_parser("promote")
    p.add_argument("lab_id")
    p.add_argument("--tex", required=True, help="e.g. tex_docs/labs/my_topic")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_promote)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
