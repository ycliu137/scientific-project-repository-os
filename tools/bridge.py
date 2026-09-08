#!/usr/bin/env python3
"""Reach sibling repos (source / pipeline / data / paper). No fifth control API.

Examples:
  python3 tools/bridge.py status
  python3 tools/bridge.py resolve source skill
  python3 tools/bridge.py run source -- pytest -q
  python3 tools/bridge.py run data -- python preprocess/example.py
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from os_config import (  # noqa: E402
    SIBLING_ORDER,
    _DEFAULT_ENV,
    iter_enabled_siblings,
    os_pack,
    sibling_root,
    siblings_cfg,
)


def _pick(name: str | None) -> tuple[str, Path] | tuple[None, None]:
    if name:
        p = sibling_root(ROOT, name)
        if p is None or not p.is_dir():
            print(f"NO_SIBLING\t{name}", file=sys.stderr)
            return None, None
        return name, p
    p = sibling_root(ROOT, None)
    if p is None or not p.is_dir():
        print("NO_SIBLING\t(default)", file=sys.stderr)
        return None, None
    pack = os_pack(ROOT)
    label = {
        "pipeline": "source",
        "paper": "pipeline",
        "data": "source",
        "source": "pipeline",
    }.get(pack, "source")
    return label, p


def cmd_status(_: argparse.Namespace) -> int:
    pack = os_pack(ROOT)
    print(f"pack\t{pack}")
    cfg = siblings_cfg(ROOT)
    rc = 0
    for name in SIBLING_ORDER:
        entry = cfg.get(name) or {}
        env_name = str(entry.get("env") or _DEFAULT_ENV.get(name) or "")
        env_val = os.environ.get(env_name, "") if env_name else ""
        p = sibling_root(ROOT, name)
        exists = bool(p and p.is_dir())
        print(
            f"sibling.{name}\tenabled={bool(entry.get('enabled'))}\t"
            f"path={entry.get('path')}\tenv={env_name}={env_val}\t"
            f"resolved={p if p else 'NONE'}\texists={exists}"
        )
        if entry.get("enabled") and not exists:
            rc = 1
        if exists and p is not None:
            skill = p / "SKILL.md"
            nav = p / "tools" / "nav.py"
            print(f"  skill={skill.is_file()}\tnav={nav.is_file()}")
    enabled = iter_enabled_siblings(ROOT)
    print(f"enabled_count\t{len(enabled)}")
    return rc


def cmd_resolve(args: argparse.Namespace) -> int:
    parts = list(args.parts)
    repo = args.repo
    if repo is None and parts and parts[0] in SIBLING_ORDER:
        repo = parts.pop(0)
    if not parts:
        print("usage: bridge.py resolve [source|pipeline|data|paper] <query>", file=sys.stderr)
        return 2
    query = parts[0]
    name, sib = _pick(repo)
    if sib is None:
        return 2
    nav = sib / "tools" / "nav.py"
    if not nav.is_file():
        print(f"SIBLING_HAS_NO_NAV\t{name}\t{sib}", file=sys.stderr)
        return 2
    print(f"REPO\t{name}\t{sib}")
    return subprocess.call([sys.executable, str(nav), "resolve", query], cwd=str(sib))


def cmd_how_to_run(args: argparse.Namespace) -> int:
    repo = args.repo
    alias = args.alias
    if repo is None and alias in SIBLING_ORDER:
        repo, alias = alias, ""
    name, sib = _pick(repo)
    if sib is None:
        return 2
    print(f"RUN_IN_SIBLING_CWD\t{name}\t{sib}")
    print(f"python3 tools/bridge.py run {name} -- <argv>")
    nav = sib / "tools" / "nav.py"
    if nav.is_file() and alias:
        return subprocess.call(
            [sys.executable, str(nav), "resolve", alias],
            cwd=str(sib),
        )
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    argv = list(args.argv)
    repo = args.repo
    if repo is None and argv and argv[0] in SIBLING_ORDER:
        repo = argv.pop(0)
    if argv[:1] == ["--"]:
        argv = argv[1:]
    name, sib = _pick(repo)
    if sib is None:
        return 2
    if not argv:
        print("usage: bridge.py run source -- pytest -q", file=sys.stderr)
        return 2
    print(f"RUN\t{name}\t{' '.join(argv)}\tcwd={sib}", flush=True)
    return subprocess.call(argv, cwd=str(sib))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(func=cmd_status)

    p = sub.add_parser("resolve")
    p.add_argument("--repo", default=None, choices=list(SIBLING_ORDER))
    p.add_argument("parts", nargs="+")
    p.set_defaults(func=cmd_resolve)

    p = sub.add_parser("how-to-run")
    p.add_argument("--repo", default=None, choices=list(SIBLING_ORDER))
    p.add_argument("alias", nargs="?", default="")
    p.set_defaults(func=cmd_how_to_run)

    p = sub.add_parser("run")
    p.add_argument("--repo", default=None, choices=list(SIBLING_ORDER))
    p.add_argument("argv", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_run)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
