#!/usr/bin/env python3
"""Navigate this repo (+ optional sibling) without grepping the tree.

Examples:
  python3 tools/nav.py resolve project_api
  python3 tools/nav.py resolve H_000001
  python3 tools/nav.py search experiment
  python3 tools/nav.py anywhere pytest
  python3 tools/nav.py rebuild
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from os_config import iter_enabled_siblings, sibling_root  # noqa: E402

INDEX = ROOT / "index"
FILES_JSON = INDEX / "nav_files.json"
ALIASES_JSON = INDEX / "nav_aliases.json"

HOW_TO_RUN: dict[str, str] = {
    "project_api": "python3 tools/project_api.py resolve H_000001",
    "code_bridge": "python3 tools/bridge.py status",
    "bridge": "python3 tools/bridge.py status",
    "check_project": "python3 tools/check_project.py",
    "nav": "python3 tools/nav.py resolve <id-or-alias>",
    "reindex": "python3 tools/project_api.py reindex",
    "apply_to_repo": "python3 tools/apply_to_repo.py --help",
}


def _load() -> tuple[dict, dict]:
    if not FILES_JSON.is_file() or not ALIASES_JSON.is_file():
        print("ERROR: nav index missing. Run: python3 tools/nav.py rebuild", file=sys.stderr)
        raise SystemExit(2)
    return (
        json.loads(FILES_JSON.read_text(encoding="utf-8")),
        json.loads(ALIASES_JSON.read_text(encoding="utf-8")),
    )


def _norm(q: str) -> str:
    return q.strip().replace("-", "_").replace(" ", "_")


def resolve_alias(query: str, aliases: dict) -> list[str]:
    raw = query.strip()
    keys = [raw, raw.lower(), _norm(raw), _norm(raw).lower(), raw.upper()]
    seen: list[str] = []
    amap = aliases.get("aliases", {})
    for k in keys:
        for path in amap.get(k, []):
            if path not in seen:
                seen.append(path)
    cand = ROOT / raw
    if cand.is_file():
        rel = cand.relative_to(ROOT).as_posix()
        if rel not in seen:
            seen.insert(0, rel)
    return seen


def search(query: str, files_blob: dict, kind: str | None = None, limit: int = 30) -> list[dict]:
    q = query.lower()
    hits: list[dict] = []
    for f in files_blob.get("files", []):
        if kind and f.get("kind") != kind:
            continue
        blob = " ".join(
            [f.get("path", ""), f.get("basename", ""), f.get("stem", ""), f.get("tier", "")]
        ).lower()
        if q in blob:
            hits.append(f)
        if len(hits) >= limit:
            break
    return hits


def cmd_resolve(args: argparse.Namespace) -> int:
    files_blob, aliases = _load()
    paths = resolve_alias(args.query, aliases)
    if not paths:
        hits = search(args.query, files_blob, limit=10)
        if not hits:
            print(f"NOT_FOUND\t{args.query}")
            return 1
        print(f"FALLBACK_SEARCH\t{args.query}\thits={len(hits)}")
        for h in hits:
            print(f"{h['path']}\tkind={h['kind']}\ttier={h['tier']}")
        return 0
    print(f"RESOLVED\there\t{args.query}\tcount={len(paths)}")
    by_path = {f["path"]: f for f in files_blob.get("files", [])}
    for p in paths:
        meta = by_path.get(p, {})
        exists = (ROOT / p).exists()
        print(f"{p}\texists={exists}\tkind={meta.get('kind', '?')}\ttier={meta.get('tier', '?')}")
    qn = _norm(args.query).lower()
    if qn in HOW_TO_RUN:
        print(f"HOW_TO_RUN\t{HOW_TO_RUN[qn]}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    files_blob, _ = _load()
    hits = search(args.query, files_blob, kind=args.kind, limit=args.limit)
    print(f"SEARCH\there\t{args.query}\thits={len(hits)}")
    for h in hits:
        print(f"{h['path']}\tkind={h['kind']}\ttier={h['tier']}")
    return 0 if hits else 1


def _sibling_nav(query: str, repo: str | None = None) -> int:
    sib = sibling_root(ROOT, repo)
    if sib is None or not sib.is_dir():
        print("NO_SIBLING\tset os.yaml siblings.<name>.enabled / path", file=sys.stderr)
        return 2
    nav = sib / "tools" / "nav.py"
    if not nav.is_file():
        print(f"SIBLING_HAS_NO_NAV\t{sib}", file=sys.stderr)
        return 2
    return subprocess.call([sys.executable, str(nav), "resolve", query], cwd=str(sib))


def cmd_sibling(args: argparse.Namespace) -> int:
    return _sibling_nav(args.query, repo=args.repo)


def cmd_anywhere(args: argparse.Namespace) -> int:
    files_blob, aliases = _load()
    paths = resolve_alias(args.query, aliases)
    if paths:
        print(f"HIT\there\t{args.query}")
        for p in paths:
            print(f"here:{p}")
        return 0
    hits = search(args.query, files_blob, limit=5)
    if hits:
        print(f"HIT\there_search\t{args.query}")
        for h in hits:
            print(f"here:{h['path']}")
        return 0
    for name, sib in iter_enabled_siblings(ROOT):
        print(f"TRY_SIBLING\t{name}\t{args.query}", flush=True)
        nav = sib / "tools" / "nav.py"
        if not nav.is_file():
            continue
        rc = subprocess.call([sys.executable, str(nav), "resolve", args.query], cwd=str(sib))
        if rc == 0:
            return 0
    return _sibling_nav(args.query)


def cmd_rebuild(_: argparse.Namespace) -> int:
    rc = subprocess.call([sys.executable, str(ROOT / "tools" / "build_nav_index.py")])
    if rc != 0:
        return rc
    for name, sib in iter_enabled_siblings(ROOT):
        builder = sib / "tools" / "build_nav_index.py"
        if builder.is_file():
            print(f"--- rebuilding sibling {name} nav index ---")
            rc2 = subprocess.call([sys.executable, str(builder)], cwd=str(sib))
            if rc2 != 0:
                return rc2
    return 0


def cmd_modules(_: argparse.Namespace) -> int:
    _, aliases = _load()
    keys = sorted(aliases.get("aliases", {}).keys())
    prefer = [k for k in keys if k.startswith(("H_", "EXP_", "CL_", "S_", "R_", "F_"))]
    short = [k for k in keys if "/" not in k and len(k) < 40][:60]
    print(f"OBJECT_IDS\t{len(prefer)}")
    for k in prefer[:40]:
        print(f"{k}\t{aliases['aliases'][k][0]}")
    print(f"SHORT_ALIASES_SAMPLE\t{min(40, len(short))}")
    for k in short[:40]:
        print(f"{k}\t{aliases['aliases'][k][0]}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("resolve", help="Resolve object ID / alias / path")
    p.add_argument("query")
    p.set_defaults(func=cmd_resolve)

    p = sub.add_parser("search", help="Substring search indexed paths")
    p.add_argument("query")
    p.add_argument("--kind", choices=["cli", "lib", "doc", "config", "file"])
    p.add_argument("--limit", type=int, default=30)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("sibling", help="Resolve inside a sibling repo")
    p.add_argument("query")
    p.add_argument("--repo", default=None, help="source|pipeline|data|paper")
    p.add_argument("-v", "--verbose", action="store_true")
    p.set_defaults(func=cmd_sibling)

    p = sub.add_parser("anywhere", help="This repo, then sibling")
    p.add_argument("query")
    p.set_defaults(func=cmd_anywhere)

    sub.add_parser("modules", help="List object IDs / aliases").set_defaults(func=cmd_modules)
    sub.add_parser("rebuild", help="Rebuild nav indexes").set_defaults(func=cmd_rebuild)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
