#!/usr/bin/env python3
"""Write-through API: create / list / resolve / reindex / context / inventory."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from os_config import load_os, project_slug  # noqa: E402

OBJECTS = ROOT / "objects"
INDEX_DIR = ROOT / "index"
DB_PATH = INDEX_DIR / "objects.db"
REL_DB_PATH = INDEX_DIR / "relations.db"
INVENTORY_PATH = INDEX_DIR / "domain_inventory.generated.yaml"

TYPE_DIR = {
    "hypothesis": "hypotheses",
    "experiment": "experiments",
    "claim": "claims",
    "source": "sources",
    "result": "results",
    "failure": "failures",
}

TYPE_PREFIX = {
    "hypothesis": "H_",
    "experiment": "EXP_",
    "claim": "CL_",
    "source": "S_",
    "result": "R_",
    "failure": "F_",
}

EMPTY_LINKS = {
    "experiments": [],
    "results": [],
    "claims": [],
    "sources": [],
    "hypotheses": [],
    "failures": [],
    "parents": [],
    "children": [],
    "supported_by": [],
    "contradicted_by": [],
    "promoted_to": [],
    "related": [],
}

TASK_SKILLS: dict[str, list[str]] = {
    "bootstrap": ["skills/bootstrap.md", "skills/runtime-env.md", "skills/language.md", "skills/notation.md"],
    "env": ["skills/runtime-env.md", "skills/code-change.md", "skills/bootstrap.md"],
    "learning": ["skills/consult-plan.md", "skills/adding-knowledge.md", "skills/pipeline-entry.md", "skills/language.md", "skills/notation.md"],
    "experiment": ["skills/consult-plan.md", "skills/adding-knowledge.md", "skills/pipeline-entry.md", "skills/pipeline-modules.md", "skills/code-change.md", "skills/notation.md"],
    "pipeline": ["skills/pipeline-entry.md", "skills/pipeline-modules.md", "skills/code-change.md", "skills/change-report.md", "skills/notation.md"],
    "literature": ["skills/consult-plan.md", "skills/adding-knowledge.md", "skills/reference-papers.md", "skills/pipeline-entry.md"],
    "lab": ["skills/backend-lab.md", "skills/tex-docs.md", "skills/code-change.md", "skills/pipeline-entry.md", "skills/notation.md"],
    "slides": ["skills/slides.md", "skills/journal-club-slides.md", "skills/language.md", "skills/notation.md", "skills/pipeline-entry.md"],
    "data": ["skills/consult-plan.md", "skills/data-management.md"],
    "meeting": ["skills/meeting-record.md", "skills/language.md", "skills/tex-docs.md", "skills/consult-plan.md"],
    "tex": ["skills/tex-docs.md", "skills/language.md", "skills/notation.md", "skills/change-report.md"],
    "write": ["skills/consult-plan.md", "skills/paper-entry.md", "skills/reference-papers.md", "skills/language.md", "skills/notation.md", "skills/change-report.md"],
    "notation": ["skills/notation.md", "docs/NOTATION.md", "skills/tex-docs.md", "skills/code-change.md"],
    "evolution": ["skills/consult-plan.md", "skills/evolution.md", "skills/language.md", "skills/notation.md"],
    "retrieval": ["skills/retrieval.md"],
}

SKIP_OBJECT_YAML = {"SKILL.md"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def connect() -> sqlite3.Connection:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS objects (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            status TEXT NOT NULL,
            path TEXT NOT NULL,
            parent_path TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def connect_relations() -> sqlite3.Connection:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(REL_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS relations (
            src_id TEXT NOT NULL,
            rel TEXT NOT NULL,
            dst_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (src_id, rel, dst_id)
        )
        """
    )
    conn.commit()
    return conn


def next_id(conn: sqlite3.Connection, type_name: str) -> str:
    prefix = TYPE_PREFIX[type_name]
    n = 1
    rows = conn.execute(
        "SELECT id FROM objects WHERE type=? ORDER BY id DESC",
        (type_name,),
    ).fetchall()
    for (oid,) in rows:
        if not oid.startswith(prefix):
            continue
        m = re.search(r"(\d+)$", oid)
        if m:
            n = max(n, int(m.group(1)) + 1)
            break
    folder = OBJECTS / TYPE_DIR[type_name]
    if folder.exists():
        for p in folder.glob(f"{prefix}[0-9]*.yaml"):
            m = re.search(r"(\d+)$", p.stem)
            if m:
                n = max(n, int(m.group(1)) + 1)
    return f"{prefix}{n:06d}"


def dump_yaml(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(data)
    body = payload.pop("body", "") or ""
    payload.pop("_path", None)
    if yaml is None:
        lines = ["---"]
        for k, v in payload.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{k}: {json.dumps(v, ensure_ascii=False)}")
            else:
                lines.append(f"{k}: {v}")
        lines.append("---")
        lines.append("")
        lines.append(str(body))
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    text = yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)
    path.write_text(f"---\n{text}---\n\n{body}\n", encoding="utf-8")


def load_object_file(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    meta_raw = parts[1]
    body = parts[2].lstrip("\n")
    if yaml is not None:
        meta = yaml.safe_load(meta_raw) or {}
    else:
        meta = {}
        for line in meta_raw.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    if not isinstance(meta, dict):
        return None
    meta["body"] = body
    meta["_path"] = str(path.relative_to(ROOT))
    return meta


def path_up_ok(parent_path: str) -> bool:
    slug = project_slug(ROOT)
    parts = Path(parent_path).parts
    return bool(parts) and parts[0] == slug


def path_up_chain(parent_path: str) -> list[str]:
    p = Path(parent_path)
    chain = [str(p)]
    while p.parent != p:
        p = p.parent
        chain.append(str(p) if str(p) != "." else p.as_posix())
    return chain


def register(conn: sqlite3.Connection, obj: dict, rel_path: str) -> None:
    conn.execute(
        """
        INSERT INTO objects(id, type, status, path, parent_path, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          type=excluded.type,
          status=excluded.status,
          path=excluded.path,
          parent_path=excluded.parent_path,
          updated_at=excluded.updated_at
        """,
        (
            obj["id"],
            obj["type"],
            obj.get("status", "draft"),
            rel_path,
            obj["parent_path"],
            obj.get("updated_at", utc_now()),
        ),
    )
    conn.commit()


def collect_domain_inventory(conn: sqlite3.Connection | None = None) -> dict[str, Any]:
    close = False
    if conn is None:
        conn = connect()
        close = True
    domains: dict[str, Any] = {}
    total = 0
    for type_name, folder in TYPE_DIR.items():
        row = conn.execute(
            "SELECT COUNT(*) FROM objects WHERE type=?",
            (type_name,),
        ).fetchone()
        n = int(row[0]) if row else 0
        total += n
        domains[folder] = {"type": type_name, "count": n, "status": "live" if n else "scaffold"}
    if close:
        conn.close()
    return {"total_objects": total, "domains": domains}


def write_domain_inventory(conn: sqlite3.Connection | None = None) -> Path:
    inv = collect_domain_inventory(conn)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Auto-generated by tools/project_api.py reindex/save. Do not hand-edit.",
        f"generated_at: {utc_now()}",
        f"total_objects: {inv['total_objects']}",
        "domains:",
    ]
    for folder, entry in inv["domains"].items():
        lines.append(f"  {folder}:")
        lines.append(f"    type: {entry['type']}")
        lines.append(f"    count: {entry['count']}")
        lines.append(f"    status: {entry['status']}")
    lines.append("")
    INVENTORY_PATH.write_text("\n".join(lines), encoding="utf-8")
    return INVENTORY_PATH


def compact_domain_inventory(inv: dict[str, Any] | None = None) -> dict[str, Any]:
    inv = inv or collect_domain_inventory()
    live = {k: v["count"] for k, v in inv["domains"].items() if v["count"]}
    scaffold = [k for k, v in inv["domains"].items() if v["count"] == 0]
    return {
        "total_objects": inv["total_objects"],
        "live": live,
        "scaffold": scaffold,
        "census": "index/domain_inventory.generated.yaml",
        "do_not_bulk_fill_scaffold": True,
    }


def base_object(
    oid: str,
    type_name: str,
    *,
    title: str,
    body: str = "",
    status: str = "draft",
    confidence: float | None = None,
    provenance: str = "ai",
) -> dict:
    now = utc_now()
    slug = project_slug(ROOT)
    folder = TYPE_DIR[type_name]
    obj: dict[str, Any] = {
        "id": oid,
        "type": type_name,
        "status": status,
        "confidence": confidence,
        "created_at": now,
        "updated_at": now,
        "provenance": provenance,
        "parent_path": f"{slug}/objects/{folder}",
        "title": title,
        "links": {k: list(v) for k, v in EMPTY_LINKS.items()},
        "body": body,
    }
    if type_name == "experiment":
        obj["run_dir"] = f"outputs/{oid}"
    return obj


def save_object(obj: dict) -> Path:
    type_name = obj["type"]
    rel = Path("objects") / TYPE_DIR[type_name] / f"{obj['id']}.yaml"
    dump_yaml(dict(obj), ROOT / rel)
    conn = connect()
    register(conn, obj, str(rel))
    write_domain_inventory(conn)
    conn.close()
    return rel


def _sync_relations_from_objects() -> int:
    rconn = connect_relations()
    rconn.execute("DELETE FROM relations")
    n = 0
    now = utc_now()
    hints = {
        "experiments": "tested_by",
        "results": "has_result",
        "claims": "claims",
        "sources": "cites",
        "hypotheses": "tests",
        "failures": "failed_as",
        "parents": "derived_from",
        "children": "parent_of",
        "supported_by": "supported_by",
        "contradicted_by": "contradicted_by",
        "related": "related_to",
        "promoted_to": "promoted_to",
    }
    if OBJECTS.is_dir():
        for path in OBJECTS.rglob("*.yaml"):
            if path.name in SKIP_OBJECT_YAML or path.name.upper().startswith("SKILL"):
                continue
            meta = load_object_file(path)
            if not meta or "id" not in meta:
                continue
            src = meta["id"]
            links = meta.get("links") or {}
            for slot, destinations in links.items():
                if not isinstance(destinations, list):
                    continue
                rel = hints.get(slot, slot)
                for dst in destinations:
                    if not isinstance(dst, str) or not dst:
                        continue
                    rconn.execute(
                        """
                        INSERT INTO relations(src_id, rel, dst_id, created_at)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(src_id, rel, dst_id) DO NOTHING
                        """,
                        (src, rel, dst, now),
                    )
                    n += 1
    rconn.commit()
    rconn.close()
    return n


def cmd_init_db(_: argparse.Namespace) -> int:
    connect().close()
    connect_relations().close()
    print(f"initialized {DB_PATH}")
    print(f"initialized {REL_DB_PATH}")
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    if args.type not in TYPE_DIR:
        print(f"unknown type: {args.type}", file=sys.stderr)
        return 2
    conn = connect()
    oid = next_id(conn, args.type)
    conn.close()
    obj = base_object(
        oid,
        args.type,
        title=args.title,
        body=args.body or "",
        status=args.status,
        confidence=args.confidence,
        provenance=args.provenance,
    )
    rel = save_object(obj)
    print(oid)
    print(rel)
    return 0


def cmd_link(args: argparse.Namespace) -> int:
    rconn = connect_relations()
    rconn.execute(
        """
        INSERT INTO relations(src_id, rel, dst_id, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(src_id, rel, dst_id) DO UPDATE SET created_at=excluded.created_at
        """,
        (args.src, args.rel, args.dst, utc_now()),
    )
    rconn.commit()
    rconn.close()
    print(f"{args.src} -[{args.rel}]-> {args.dst}")
    return 0


def cmd_list(_: argparse.Namespace) -> int:
    conn = connect()
    rows = conn.execute(
        "SELECT id, type, status, path, parent_path FROM objects ORDER BY id"
    ).fetchall()
    conn.close()
    if not rows:
        print("(empty)")
        return 0
    for r in rows:
        print("\t".join(r))
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    conn = connect()
    row = conn.execute(
        "SELECT id, type, status, path, parent_path FROM objects WHERE id=?",
        (args.id,),
    ).fetchone()
    conn.close()
    if not row:
        print(f"not found: {args.id}", file=sys.stderr)
        return 1
    print("\t".join(row))
    return 0


def cmd_path_up(args: argparse.Namespace) -> int:
    conn = connect()
    row = conn.execute(
        "SELECT parent_path FROM objects WHERE id=?",
        (args.id,),
    ).fetchone()
    conn.close()
    if not row:
        print(f"not found: {args.id}", file=sys.stderr)
        return 1
    chain = path_up_chain(row[0])
    for c in chain:
        print(c)
    if not path_up_ok(row[0]):
        print(f"ERROR: cannot path_up to {project_slug(ROOT)}", file=sys.stderr)
        return 2
    return 0


def cmd_reindex(_: argparse.Namespace) -> int:
    conn = connect()
    conn.execute("DELETE FROM objects")
    conn.commit()
    n = 0
    if OBJECTS.is_dir():
        for path in OBJECTS.rglob("*.yaml"):
            if path.name.upper().startswith("SKILL") or path.name in SKIP_OBJECT_YAML:
                continue
            meta = load_object_file(path)
            if not meta or "id" not in meta or "parent_path" not in meta:
                continue
            rel = str(path.relative_to(ROOT))
            register(conn, meta, rel)
            n += 1
    write_domain_inventory(conn)
    conn.close()
    rn = _sync_relations_from_objects()
    print(f"reindexed {n} objects")
    print(f"synced {rn} relation edges")
    print(f"wrote {INVENTORY_PATH.relative_to(ROOT)}")
    return 0


def cmd_inventory(_: argparse.Namespace) -> int:
    inv = collect_domain_inventory()
    write_domain_inventory()
    print(json.dumps(compact_domain_inventory(inv), indent=2, ensure_ascii=False))
    return 0


def _missing_what() -> list[str]:
    issues: list[str] = []
    conn = connect()
    rows = conn.execute(
        "SELECT id, type, status, path, parent_path FROM objects ORDER BY id"
    ).fetchall()
    conn.close()
    for oid, typ, status, path, parent in rows:
        if not path_up_ok(parent):
            issues.append(f"path_up_fail:{oid}")
        full = ROOT / path
        meta = load_object_file(full) if full.is_file() else None
        if meta is None:
            issues.append(f"unreadable:{oid}")
            continue
        links = meta.get("links") or {}
        if typ == "hypothesis" and status in {"active", "open"}:
            if not (links.get("experiments") or []):
                issues.append(f"hypothesis_untested:{oid}")
        if typ == "claim" and status in {"accepted", "established"}:
            if not (links.get("results") or links.get("experiments") or []):
                issues.append(f"claim_accepted_without_result:{oid}")
        if typ == "experiment" and status in {"running", "done"}:
            if not (links.get("results") or []):
                issues.append(f"experiment_missing_result:{oid}")
    return issues


def cmd_completeness(_: argparse.Namespace) -> int:
    issues = _missing_what()
    if not issues:
        print("COMPLETENESS_OK")
        return 0
    print(f"COMPLETENESS_ISSUES\t{len(issues)}")
    for line in issues:
        print(line)
    return 0


def cmd_context(args: argparse.Namespace) -> int:
    key = (args.task or "learning").strip().lower()
    skills = TASK_SKILLS.get(key, TASK_SKILLS["learning"])
    missing_files = [s for s in skills if not (ROOT / s).is_file()]
    pointer = ROOT / "workspace" / "current" / "NEXT_ACTION.yaml"
    compact: dict[str, Any] = {}
    if pointer.is_file() and yaml is not None:
        try:
            compact = yaml.safe_load(pointer.read_text(encoding="utf-8")) or {}
        except Exception:
            compact = {}
    payload = {
        "task": key,
        "read_constitution": ["SKILL.md", "MAP.md"],
        "read_skills_now": skills,
        "do_not_pre_read": "other skills/*.md unless listed above",
        "compact_state": {
            "current_focus": compact.get("current_focus"),
            "next_actions": compact.get("next_actions"),
            "do_not": compact.get("do_not"),
        },
        "missing_what": _missing_what(),
        "missing_skill_files": missing_files,
        "domain_inventory": compact_domain_inventory(),
        "os": {
            "pack": (load_os(ROOT).get("os") or {}).get("pack"),
            "slug": project_slug(ROOT),
        },
        "completeness_note": (
            "Gaps the index can see. Empty scaffold domains are intentional — not a fill-now gap."
        ),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Write-through project API")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init-db").set_defaults(func=cmd_init_db)
    sub.add_parser("list").set_defaults(func=cmd_list)
    sub.add_parser("reindex").set_defaults(func=cmd_reindex)
    sub.add_parser("inventory").set_defaults(func=cmd_inventory)
    sub.add_parser("completeness").set_defaults(func=cmd_completeness)

    p = sub.add_parser("context")
    p.add_argument("--task", default="learning")
    p.set_defaults(func=cmd_context)

    p = sub.add_parser("create")
    p.add_argument("--type", required=True, choices=sorted(TYPE_DIR))
    p.add_argument("--title", required=True)
    p.add_argument("--body", default="")
    p.add_argument("--provenance", default="ai", choices=["human", "ai", "assimilated"])
    p.add_argument("--status", default="draft")
    p.add_argument("--confidence", type=float, default=None)
    p.set_defaults(func=cmd_create)

    p = sub.add_parser("link")
    p.add_argument("--src", required=True)
    p.add_argument("--rel", required=True)
    p.add_argument("--dst", required=True)
    p.set_defaults(func=cmd_link)

    p = sub.add_parser("resolve")
    p.add_argument("id")
    p.set_defaults(func=cmd_resolve)

    p = sub.add_parser("path-up")
    p.add_argument("--id", required=True)
    p.set_defaults(func=cmd_path_up)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
