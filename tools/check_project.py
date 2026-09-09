#!/usr/bin/env python3
"""Integrity gate. Exit 0 = VALID or VALID_WITH_WARN. Non-zero = INVALID.

strictness from os.yaml: warn (overlay) vs error (new instance can tighten later).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from os_config import (  # noqa: E402
    include_roots,
    legacy_roots,
    load_os,
    os_pack,
    project_slug,
    strictness as os_strictness,
)
from project_api import (  # noqa: E402
    OBJECTS,
    load_object_file,
    path_up_ok,
)

ID_RE = re.compile(r"^(H|EXP|CL|S|R|F)_\d{6}$")

CORE_FILES = [
    ROOT / "SKILL.md",
    ROOT / "MAP.md",
    ROOT / "COLD_START.md",
    ROOT / "os.yaml",
    ROOT / "AGENTS.md",
    ROOT / "skills" / "consult-plan.md",
    ROOT / "skills" / "retrieval.md",
    ROOT / "skills" / "adding-knowledge.md",
    ROOT / "skills" / "change-report.md",
    ROOT / "skills" / "code-change.md",
    ROOT / "skills" / "runtime-env.md",
    ROOT / "skills" / "language.md",
    ROOT / "skills" / "notation.md",
    ROOT / "tools" / "nav.py",
    ROOT / "tools" / "project_api.py",
    ROOT / "workspace" / "current" / "NEXT_ACTION.yaml",
]

MODULE_README_HEADINGS = ("Purpose", "Inputs", "Outputs", "Relations", "How to run", "Path contract")
CREATE_SCRIPT_RE = re.compile(r"^create_.+\.sh$")
CATALOG_SCRIPT_RE = re.compile(r"^script:\s+(\S+)")


def _check_env_folder() -> list[str]:
    """create_*.sh must be listed in catalog.yaml (pipeline/source). Missing env/ is WARN."""
    warnings: list[str] = []
    pack = os_pack(ROOT)
    if pack not in ("pipeline", "source"):
        return warnings
    env = ROOT / "env"
    if not env.is_dir():
        warnings.append("env/ missing — one create_*.sh per runtime (skills/runtime-env.md)")
        return warnings
    if not (env / "README.md").is_file():
        warnings.append("env/README.md missing")
    catalog = env / "catalog.yaml"
    catalog_text = catalog.read_text(encoding="utf-8") if catalog.is_file() else ""
    if not catalog.is_file():
        warnings.append("env/catalog.yaml missing")
    for script in sorted(env.glob("create_*.sh")):
        if not CREATE_SCRIPT_RE.match(script.name):
            continue
        if catalog_text and script.name not in catalog_text:
            warnings.append(f"env/{script.name} not listed in env/catalog.yaml")
        if not os.access(script, os.X_OK):
            warnings.append(f"env/{script.name} is not executable")
    if catalog_text:
        for line in catalog_text.splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            m = CATALOG_SCRIPT_RE.match(s)
            if not m:
                continue
            rel = m.group(1).strip("\"'")
            path = ROOT / rel if not rel.startswith("/") else Path(rel)
            if not path.is_file():
                alt = env / Path(rel).name
                if not alt.is_file():
                    warnings.append(f"env/catalog.yaml script missing: {rel}")
    return warnings


def _check_pipeline_modules() -> tuple[list[str], list[str]]:
    """Each pipelines/<module>/ (except _TEMPLATE) needs a structured README."""
    errors: list[str] = []
    warnings: list[str] = []
    if os_pack(ROOT) != "pipeline":
        return errors, warnings
    root = ROOT / "pipelines"
    if not root.is_dir():
        return errors, warnings
    catalog = root / "README.md"
    if not catalog.is_file():
        warnings.append("pipelines/README.md missing — module catalog (skills/pipeline-modules.md)")
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith(("_", ".")):
            continue
        readme = child / "README.md"
        rel = child.relative_to(ROOT).as_posix()
        if not readme.is_file():
            errors.append(f"pipeline module {rel}/ has no README.md — copy pipelines/_TEMPLATE/")
            continue
        text = readme.read_text(encoding="utf-8")
        missing = [h for h in MODULE_README_HEADINGS if f"## {h}" not in text]
        if missing:
            warnings.append(
                f"{rel}/README.md missing headings: {', '.join(missing)} (skills/pipeline-modules.md)"
            )
        if catalog.is_file() and child.name not in catalog.read_text(encoding="utf-8"):
            warnings.append(f"pipelines/README.md catalog does not mention module {child.name}")
    return errors, warnings


SKIP_INDEX_NAMES = {
    "nav_files.json",
    "nav_aliases.json",
    "tree.generated.yaml",
    "domain_inventory.generated.yaml",
    ".gitkeep",
}


def _check_domain_map() -> list[str]:
    """MAP is a contract table — require census pointer only; no scaffold/live rows."""
    errors: list[str] = []
    map_path = ROOT / "MAP.md"
    if not map_path.is_file():
        return ["missing MAP.md"]
    map_text = map_path.read_text(encoding="utf-8")
    if "index/domain_inventory.generated.yaml" not in map_text:
        errors.append("MAP.md must point at index/domain_inventory.generated.yaml as census")
    # Reject old status tables that pretend empty domains are "open projects"
    if re.search(r"\|\s*`objects/[^`]+/`\s*\|\s*[^|]*\|\s*scaffold\s*\|", map_text, re.I):
        errors.append(
            "MAP.md must not list empty-domain scaffold/live status — census is inventory only"
        )
    return errors


def _unindexed_files(indexed_paths: set[str]) -> list[str]:
    missing: list[str] = []
    skip_dirs = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules"}
    skip_suf = {".pyc", ".pyo", ".db", ".db-journal", ".db-wal", ".db-shm"}
    roots = include_roots(ROOT)
    extra = ["SKILL.md", "AGENTS.md", "MAP.md", "COLD_START.md", "os.yaml", "README.md"]
    candidates: list[Path] = []
    for name in extra:
        p = ROOT / name
        if p.is_file():
            candidates.append(p)
    for r in roots:
        base = ROOT / r
        if not base.exists():
            continue
        if r == "index":
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if any(part in skip_dirs for part in p.parts):
                continue
            if p.suffix in skip_suf or p.name in SKIP_INDEX_NAMES:
                continue
            candidates.append(p)
    for p in candidates:
        rel = p.relative_to(ROOT).as_posix()
        if rel not in indexed_paths:
            missing.append(rel)
    return sorted(missing)


def _change_report_density() -> list[str]:
    warns: list[str] = []
    cr_dir = ROOT / "docs" / "change_reports"
    if not cr_dir.is_dir():
        return warns
    required = ("why", "artifacts", "risks", "integrity")
    for path in cr_dir.glob("*.yaml"):
        if path.name.startswith("_") or path.name == "schema.yaml":
            continue
        text = path.read_text(encoding="utf-8")
        for key in required:
            if f"{key}:" not in text and f"{key} :" not in text:
                warns.append(f"thin Change Report {path.name}: missing {key}")
    return warns


def _check_notation_registry() -> list[str]:
    """Pipeline packs should keep docs/NOTATION.md (H21). Missing is WARN."""
    warnings: list[str] = []
    if os_pack(ROOT) != "pipeline":
        return warnings
    path = ROOT / "docs" / "NOTATION.md"
    if not path.is_file():
        warnings.append(
            "docs/NOTATION.md missing — docs↔code symbol map (skills/notation.md)"
        )
    return warnings


CJK_RE = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
CJK_ALLOW_PREFIXES = ("tex_docs/", "meeting_record/")
CJK_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".sh", ".txt", ".toml", ".tex", ".rst", ".cfg"}
CJK_SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules", "secrets"}


def _check_project_english() -> list[str]:
    """WARN on CJK outside tex_docs/ and meeting_record/ (H18). Always WARN, not INVALID."""
    warnings: list[str] = []
    hits = 0
    extra = ["SKILL.md", "AGENTS.md", "MAP.md", "COLD_START.md", "os.yaml", "README.md"]
    candidates: list[Path] = []
    for name in extra:
        p = ROOT / name
        if p.is_file():
            candidates.append(p)
    roots = include_roots(ROOT) or []
    for r in roots:
        base = ROOT / r
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if any(part in CJK_SKIP_DIRS for part in p.parts):
                continue
            candidates.append(p)
    seen: set[str] = set()
    for p in candidates:
        rel = p.relative_to(ROOT).as_posix()
        if rel in seen:
            continue
        seen.add(rel)
        if rel.startswith(CJK_ALLOW_PREFIXES):
            continue
        if p.suffix.lower() not in CJK_SUFFIXES:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if CJK_RE.search(text):
            warnings.append(
                f"CJK in {rel} — project language is English except tex_docs/ and meeting_record/ (skills/language.md)"
            )
            hits += 1
            if hits >= 15:
                warnings.append("further CJK files omitted from this scan")
                break
    return warnings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--strictness",
        choices=["warn", "error"],
        default=None,
        help="Override os.yaml os.strictness",
    )
    args = ap.parse_args()
    load_os(ROOT)
    mode = args.strictness or os_strictness(ROOT)
    slug = project_slug(ROOT)

    errors: list[str] = []
    warnings: list[str] = []

    for path in CORE_FILES:
        if not path.is_file():
            errors.append(f"missing CORE file: {path.relative_to(ROOT)}")

    nav_files = ROOT / "index" / "nav_files.json"
    nav_aliases = ROOT / "index" / "nav_aliases.json"
    indexed_paths: set[str] = set()
    if not nav_files.is_file() or not nav_aliases.is_file():
        warnings.append("nav index missing — run: python3 tools/nav.py rebuild")
    else:
        blob = json.loads(nav_files.read_text(encoding="utf-8"))
        indexed_paths = {f["path"] for f in blob.get("files", [])}

    db = ROOT / "index" / "objects.db"
    indexed_ids: dict[str, str] = {}
    if db.is_file():
        conn = sqlite3.connect(db)
        for oid, path, parent in conn.execute("SELECT id, path, parent_path FROM objects"):
            indexed_ids[oid] = path
            if not path_up_ok(parent):
                errors.append(f"{oid}: bad parent_path={parent!r} (need prefix {slug})")
            if not ID_RE.match(oid):
                errors.append(f"{oid}: bad id format")
            if not (ROOT / path).is_file():
                errors.append(f"{oid}: indexed path missing {path}")
        conn.close()

    if OBJECTS.is_dir():
        for path in OBJECTS.rglob("*.yaml"):
            if path.name.upper().startswith("SKILL"):
                continue
            meta = load_object_file(path)
            if meta is None:
                errors.append(f"unreadable object {path.relative_to(ROOT)}")
                continue
            oid = str(meta.get("id") or "")
            if oid and oid not in indexed_ids:
                errors.append(f"{oid}: file not in objects.db — run project_api reindex")
            typ = meta.get("type")
            if typ == "claim":
                links = meta.get("links") or {}
                promoted = links.get("promoted_to") or []
                if any(str(x).startswith("R_") for x in promoted) and not (
                    links.get("results") or links.get("experiments")
                ):
                    errors.append(f"{oid}: claim promoted to result without experiment/result links")

    errors.extend(_check_domain_map() if os_pack(ROOT) == "pipeline" else [])
    mod_err, mod_warn = _check_pipeline_modules()
    errors.extend(mod_err)
    warnings.extend(mod_warn)
    warnings.extend(_check_env_folder())
    warnings.extend(_change_report_density())
    warnings.extend(_check_project_english())
    warnings.extend(_check_notation_registry())

    if indexed_paths:
        missing = _unindexed_files(indexed_paths)
        legacy = set(legacy_roots(ROOT))
        for rel in missing:
            if any(rel == lg or rel.startswith(lg.rstrip("/") + "/") for lg in legacy):
                warnings.append(f"legacy unindexed (ok): {rel}")
                continue
            msg = f"unindexed file: {rel} — run tools/nav.py rebuild"
            if mode == "error":
                errors.append(msg)
            else:
                warnings.append(msg)

    for w in warnings:
        print(f"WARN\t{w}")
    for e in errors:
        print(f"ERROR\t{e}")

    if errors:
        print("INVALID")
        return 1
    if warnings:
        print("VALID_WITH_WARN")
        return 0
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
