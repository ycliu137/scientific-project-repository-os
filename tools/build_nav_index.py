#!/usr/bin/env python3
"""Build navigation index: files + aliases (including object IDs).

Outputs:
  index/nav_files.json
  index/nav_aliases.json
  index/tree.generated.yaml
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from os_config import include_roots, load_os, project_slug  # noqa: E402

INDEX = ROOT / "index"
DB_PATH = INDEX / "objects.db"

INCLUDE_ROOT_FILES = (
    "SKILL.md",
    "AGENTS.md",
    "MAP.md",
    "README.md",
    "COLD_START.md",
    "os.yaml",
    "LICENSE",
    "requirements.txt",
)
SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "secrets",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".mypy_cache",
}
SKIP_SUFFIXES = {".pyc", ".pyo", ".db", ".db-journal", ".db-wal", ".db-shm"}
SKIP_BINARY = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip"}

SEED_ALIASES: dict[str, list[str]] = {
    "skill": ["SKILL.md"],
    "map": ["MAP.md"],
    "agents": ["AGENTS.md"],
    "cold_start": ["COLD_START.md"],
    "os": ["os.yaml"],
    "os_yaml": ["os.yaml"],
    "project_api": ["tools/project_api.py"],
    "nav": ["tools/nav.py"],
    "check_project": ["tools/check_project.py"],
    "integrity": ["tools/check_project.py"],
    "code_bridge": ["tools/bridge.py"],
    "bridge": ["tools/bridge.py"],
    "compile_tex_docs": ["tools/compile_tex_docs.py"],
    "pipeline_entry": ["skills/pipeline-entry.md"],
    "pipeline_modules": ["skills/pipeline-modules.md", "pipelines/README.md"],
    "code_change": ["skills/code-change.md"],
    "runtime_env": ["skills/runtime-env.md", "env/README.md", "env/catalog.yaml"],
    "language": ["skills/language.md"],
    "env_catalog": ["env/catalog.yaml"],
    "source_package": ["skills/source-package.md"],
    "data_management": ["skills/data-management.md"],
    "meeting_record": ["skills/meeting-record.md"],
    "tex_docs": ["skills/tex-docs.md", "tex_docs/README.md"],
    "apply": ["tools/apply_to_repo.py"],
    "apply_to_repo": ["tools/apply_to_repo.py"],
    "bootstrap": ["skills/bootstrap.md"],
    "consult_plan": ["skills/consult-plan.md"],
    "retrieval": ["skills/retrieval.md"],
    "adding_knowledge": ["skills/adding-knowledge.md"],
    "change_report": ["skills/change-report.md"],
    "reindex": ["skills/reindex.md"],
    "maintenance": ["skills/maintenance.md"],
    "evolution": ["skills/evolution.md"],
    "paper_entry": ["skills/paper-entry.md"],
    "master_plan": ["docs/MASTER_PLAN.md"],
    "next_action": ["workspace/current/NEXT_ACTION.yaml"],
    "plan_pointer": ["tools/plan_pointer.py"],
    "object_schema": ["protocol/OBJECT_SCHEMA.md"],
}


def _kind_for(rel: str) -> str:
    if rel.endswith(".md"):
        return "doc"
    if rel.endswith((".yaml", ".yml", ".json")):
        return "config"
    if rel.endswith(".py"):
        if rel.startswith("tools/") or rel.startswith("integrity/"):
            return "cli"
        return "lib"
    if rel.endswith(".sh"):
        return "ops"
    return "file"


def _tier_for(rel: str) -> str:
    if rel.startswith("objects/"):
        return "object"
    if rel in ("SKILL.md", "AGENTS.md", "MAP.md", "COLD_START.md", "os.yaml") or rel.startswith(
        ("skills/", "protocol/", "integrity/")
    ):
        return "control"
    if rel.startswith("tools/"):
        return "ops"
    if rel.startswith("src/"):
        return "code"
    if rel.startswith("pipelines/"):
        return "run"
    if rel.startswith("tex_docs/"):
        return "doc"
    if rel.startswith("experiments/"):
        return "run"
    if rel.startswith("env/"):
        return "ops"
    return "other"


def iter_files() -> list[Path]:
    out: list[Path] = []
    for name in INCLUDE_ROOT_FILES:
        p = ROOT / name
        if p.is_file():
            out.append(p)
    roots = include_roots(ROOT) or [
        "skills",
        "docs",
        "tex_docs",
        "tools",
        "workspace",
        "index",
        "tests",
        "env",
        "objects",
        "pipelines",
        "experiments",
    ]
    for root_name in roots:
        base = ROOT / root_name
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if any(part in SKIP_DIR_NAMES for part in p.parts):
                continue
            if p.suffix in SKIP_SUFFIXES:
                continue
            if p.suffix.lower() in SKIP_BINARY:
                continue
            out.append(p)
    return sorted(set(out), key=lambda x: str(x))


def object_aliases() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    obj_root = ROOT / "objects"
    if DB_PATH.is_file():
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("SELECT id, path FROM objects").fetchall()
        conn.close()
        for oid, path in rows:
            out.setdefault(oid, []).append(path)
            out.setdefault(oid.lower(), []).append(path)
        return out
    if obj_root.is_dir():
        for p in obj_root.rglob("*.yaml"):
            stem = p.stem
            if "_" in stem and stem.split("_")[0].isupper():
                rel = p.relative_to(ROOT).as_posix()
                out.setdefault(stem, []).append(rel)
                out.setdefault(stem.upper(), []).append(rel)
    return out


def build() -> dict:
    files: list[dict] = []
    aliases: dict[str, list[str]] = {k: list(v) for k, v in SEED_ALIASES.items()}
    prefixes = ("H_", "EXP_", "CL_", "S_", "R_", "F_")

    for path in iter_files():
        rel = path.relative_to(ROOT).as_posix()
        stem = path.stem
        entry = {
            "path": rel,
            "basename": path.name,
            "stem": stem,
            "kind": _kind_for(rel),
            "tier": _tier_for(rel),
            "suffix": path.suffix.lstrip("."),
        }
        if path.suffix == ".py":
            aliases.setdefault(stem, [])
            if rel not in aliases[stem]:
                aliases[stem].append(rel)
        elif path.suffix == ".md":
            key = stem.lower().replace("-", "_")
            aliases.setdefault(key, [])
            if rel not in aliases[key]:
                aliases[key].append(rel)
            if stem.startswith(prefixes):
                aliases.setdefault(stem, [])
                if rel not in aliases[stem]:
                    aliases[stem].append(rel)
        files.append(entry)

    for oid, paths in object_aliases().items():
        aliases.setdefault(oid, [])
        for p in paths:
            if p not in aliases[oid]:
                aliases[oid].append(p)

    clean = {k: list(dict.fromkeys(v)) for k, v in sorted(aliases.items()) if v}
    slug = project_slug(ROOT)
    return {
        "repo": slug,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "root": str(ROOT),
        "file_count": len(files),
        "alias_count": len(clean),
        "files": files,
        "aliases": clean,
    }


def write_outputs(payload: dict, quiet: bool) -> None:
    INDEX.mkdir(parents=True, exist_ok=True)
    meta = {
        "repo": payload["repo"],
        "generated_at": payload["generated_at"],
        "file_count": payload["file_count"],
        "alias_count": payload["alias_count"],
    }
    (INDEX / "nav_files.json").write_text(
        json.dumps({"meta": meta, "files": payload["files"]}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    (INDEX / "nav_aliases.json").write_text(
        json.dumps({"meta": meta, "aliases": payload["aliases"]}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    (INDEX / "tree.generated.yaml").write_text(
        "\n".join(
            [
                "# Auto-generated by tools/build_nav_index.py",
                f"root: {payload['repo']}",
                f"generated_at: {payload['generated_at']}",
                f"file_count: {payload['file_count']}",
                f"alias_count: {payload['alias_count']}",
                "seed_aliases:",
                *[f"  - {a}" for a in sorted(SEED_ALIASES)],
                "",
            ]
        ),
        encoding="utf-8",
    )
    if not quiet:
        print(f"Wrote index/nav_files.json ({payload['file_count']} files)")
        print(f"Wrote index/nav_aliases.json ({payload['alias_count']} aliases)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    load_os(ROOT)
    write_outputs(build(), quiet=args.quiet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
