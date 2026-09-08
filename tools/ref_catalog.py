#!/usr/bin/env python3
"""Reference-paper catalog for the ref sibling pack.

PDFs live in a unified gitignored store: pdfs/<Title_Slug>.pdf
Metadata lives in git: papers/<Title_Slug>/meta.yaml

Examples:
  python3 tools/ref_catalog.py slug "A Spatial Factor Identifiability Paper"
  python3 tools/ref_catalog.py list
  python3 tools/ref_catalog.py search niche
  python3 tools/ref_catalog.py validate
  python3 tools/ref_catalog.py add --title "..." --kind algorithm --pdf /path/to/file.pdf
  python3 tools/ref_catalog.py merge-pdf main.pdf si.pdf --slug Some_Title
  python3 tools/ref_catalog.py export-bib
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT / "papers"
PDFS = ROOT / "pdfs"
CATALOG = ROOT / "catalog.yaml"
BIB = ROOT / "bib" / "references.bib"

REQUIRED = (
    "id",
    "title",
    "title_slug",
    "authors",
    "venue",
    "published_at",
    "kind",
    "research_directions",
    "problem",
    "methods",
    "contribution",
    "appendix_merged",
    "added_at",
)
KINDS = {"experiment", "algorithm", "analysis", "review", "theory", "other"}

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def _load_yaml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if yaml is None:
        raise SystemExit("PyYAML required for ref_catalog (pip install pyyaml)")
    data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must be a mapping")
    return data


def _dump_yaml(data: dict) -> str:
    if yaml is None:
        raise SystemExit("PyYAML required for ref_catalog (pip install pyyaml)")
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def slugify(title: str, max_len: int = 120) -> str:
    s = title.strip()
    s = s.replace("—", "-").replace("–", "-")
    s = re.sub(r"[^\w\s\-]+", "", s, flags=re.UNICODE)
    s = re.sub(r"\s+", "_", s.strip())
    s = re.sub(r"_+", "_", s)
    s = s.strip("_")
    if not s:
        s = "untitled"
    return s[:max_len]


def pdf_relpath(slug: str) -> str:
    return f"pdfs/{slug}.pdf"


def pdf_abspath(slug: str) -> Path:
    return PDFS / f"{slug}.pdf"


def resolve_pdf(meta: dict, slug: str) -> Path:
    """Prefer meta.pdf_path; fall back to pdfs/<slug>.pdf."""
    raw = meta.get("pdf_path")
    if raw:
        p = Path(str(raw))
        if not p.is_absolute():
            p = ROOT / p
        return p
    return pdf_abspath(slug)


def next_ref_id() -> str:
    n = 1
    if CATALOG.is_file():
        cat = _load_yaml(CATALOG)
        for row in cat.get("papers") or []:
            rid = str((row or {}).get("id") or "")
            m = re.fullmatch(r"REF_(\d+)", rid)
            if m:
                n = max(n, int(m.group(1)) + 1)
    for meta in PAPERS.glob("*/meta.yaml"):
        try:
            data = _load_yaml(meta)
        except Exception:
            continue
        rid = str(data.get("id") or "")
        m = re.fullmatch(r"REF_(\d+)", rid)
        if m:
            n = max(n, int(m.group(1)) + 1)
    return f"REF_{n:06d}"


def iter_papers() -> list[tuple[Path, dict]]:
    out: list[tuple[Path, dict]] = []
    if not PAPERS.is_dir():
        return out
    for d in sorted(PAPERS.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        meta = d / "meta.yaml"
        if not meta.is_file():
            out.append((d, {}))
            continue
        try:
            out.append((d, _load_yaml(meta)))
        except Exception as e:
            out.append((d, {"_error": str(e)}))
    return out


def ensure_catalog() -> dict:
    if CATALOG.is_file():
        return _load_yaml(CATALOG)
    return {"papers": []}


def write_catalog(rows: list[dict]) -> None:
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(_dump_yaml({"papers": rows}), encoding="utf-8")


def rebuild_catalog_rows() -> list[dict]:
    rows = []
    for d, meta in iter_papers():
        if not meta or meta.get("_error"):
            continue
        rows.append(
            {
                "id": meta.get("id"),
                "title_slug": d.name,
                "title": meta.get("title"),
                "kind": meta.get("kind"),
                "cite_key": meta.get("cite_key") or "",
                "path": f"papers/{d.name}",
                "pdf_path": meta.get("pdf_path") or pdf_relpath(d.name),
            }
        )
    return rows


def cmd_slug(args: argparse.Namespace) -> int:
    print(slugify(args.title))
    return 0


def cmd_list(_: argparse.Namespace) -> int:
    papers = iter_papers()
    if not papers:
        print("EMPTY\tpapers/")
        return 0
    for d, meta in papers:
        if meta.get("_error"):
            print(f"ERROR\t{d.name}\t{meta['_error']}")
            continue
        kind = meta.get("kind", "?")
        title = meta.get("title") or d.name
        rid = meta.get("id", "?")
        pdf = "pdf" if resolve_pdf(meta, d.name).is_file() else "NO_PDF"
        print(f"{rid}\t{kind}\t{pdf}\t{d.name}\t{title}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    q = args.query.lower()
    hits = 0
    for d, meta in iter_papers():
        blob = " ".join(
            [
                d.name,
                str(meta.get("title") or ""),
                str(meta.get("problem") or ""),
                str(meta.get("contribution") or ""),
                " ".join(str(x) for x in (meta.get("methods") or [])),
                " ".join(str(x) for x in (meta.get("research_directions") or [])),
                " ".join(str(x) for x in (meta.get("tags") or [])),
                str(meta.get("kind") or ""),
            ]
        ).lower()
        if q in blob:
            hits += 1
            print(f"HIT\t{meta.get('id', '?')}\t{d.name}\t{meta.get('title', '')}")
    print(f"hits\t{hits}")
    return 0 if hits else 1


def cmd_validate(_: argparse.Namespace) -> int:
    rc = 0
    seen_ids: set[str] = set()
    seen_slugs: set[str] = set()
    for d, meta in iter_papers():
        if meta.get("_error"):
            print(f"INVALID\t{d.name}\tmeta_parse\t{meta['_error']}")
            rc = 1
            continue
        if not meta:
            print(f"INVALID\t{d.name}\tmissing_meta")
            rc = 1
            continue
        slug = str(meta.get("title_slug") or "")
        if slug and slug != d.name:
            print(f"INVALID\t{d.name}\tslug_mismatch\tmeta={slug}")
            rc = 1
        if d.name in seen_slugs:
            print(f"INVALID\t{d.name}\tduplicate_slug")
            rc = 1
        seen_slugs.add(d.name)
        rid = str(meta.get("id") or "")
        if rid in seen_ids:
            print(f"INVALID\t{d.name}\tduplicate_id\t{rid}")
            rc = 1
        if rid:
            seen_ids.add(rid)
        for key in REQUIRED:
            if key not in meta or meta.get(key) in (None, ""):
                print(f"INVALID\t{d.name}\tmissing_field\t{key}")
                rc = 1
        kind = meta.get("kind")
        if kind and kind not in KINDS:
            print(f"INVALID\t{d.name}\tbad_kind\t{kind}")
            rc = 1
        expected = pdf_relpath(d.name)
        raw = str(meta.get("pdf_path") or "")
        if raw and raw != expected and Path(raw).name != f"{d.name}.pdf":
            print(f"WARN\t{d.name}\tpdf_path_unusual\t{raw}\texpected={expected}")
        if not resolve_pdf(meta, d.name).is_file():
            print(f"WARN\t{d.name}\tmissing_pdf\t{expected}")
        if meta.get("appendix_merged") is not True:
            print(f"WARN\t{d.name}\tappendix_merged_not_true")
    if PDFS.is_dir():
        known = {d.name for d, m in iter_papers() if m and not m.get("_error")}
        for pdf in sorted(PDFS.glob("*.pdf")):
            if pdf.stem.startswith("_"):
                continue
            if pdf.stem not in known:
                print(f"WARN\t{pdf.name}\tpdf_without_meta")
    if CATALOG.is_file():
        cat = ensure_catalog()
        cat_slugs = {str(r.get("title_slug")) for r in (cat.get("papers") or []) if r}
        disk_slugs = {d.name for d, m in iter_papers() if m and not m.get("_error")}
        for s in sorted(disk_slugs - cat_slugs):
            print(f"WARN\t{s}\tnot_in_catalog")
        for s in sorted(cat_slugs - disk_slugs):
            print(f"WARN\t{s}\tcatalog_orphan")
    if rc == 0:
        print("VALID")
    return rc


def cmd_add(args: argparse.Namespace) -> int:
    title = args.title.strip()
    slug = args.slug or slugify(title)
    dest = PAPERS / slug
    if dest.exists() and not args.force:
        print(f"EXISTS\t{dest}", file=sys.stderr)
        return 2
    dest.mkdir(parents=True, exist_ok=True)
    PDFS.mkdir(parents=True, exist_ok=True)
    authors = [a.strip() for a in (args.authors or "").split(";") if a.strip()]
    methods = [m.strip() for m in (args.methods or "").split(";") if m.strip()]
    dirs = [d.strip() for d in (args.directions or "").split(";") if d.strip()]
    cite = args.cite_key or re.sub(r"[^A-Za-z0-9]", "", slug)[:40]
    rel_pdf = pdf_relpath(slug)
    meta = {
        "id": args.id or next_ref_id(),
        "title": title,
        "title_slug": slug,
        "authors": authors,
        "venue": args.venue or "",
        "published_at": args.published_at or str(date.today().year),
        "kind": args.kind,
        "research_directions": dirs,
        "problem": (args.problem or "").strip() or "TODO",
        "methods": methods,
        "contribution": (args.contribution or "").strip() or "TODO",
        "appendix_merged": bool(args.appendix_merged),
        "doi": args.doi,
        "url": args.url,
        "pdf_path": rel_pdf,
        "cite_key": cite,
        "tags": [t.strip() for t in (args.tags or "").split(";") if t.strip()],
        "pipeline_sources": [],
        "added_at": date.today().isoformat(),
        "notes": None,
    }
    (dest / "meta.yaml").write_text(_dump_yaml(meta), encoding="utf-8")
    notes = dest / "notes.md"
    if not notes.exists():
        notes.write_text("# Notes\n\n", encoding="utf-8")
    if args.pdf:
        src = Path(args.pdf).expanduser()
        if not src.is_file():
            print(f"NO_PDF\t{src}", file=sys.stderr)
            return 2
        shutil.copy2(src, pdf_abspath(slug))
        print(f"PDF\t{pdf_abspath(slug)}")
    rows = rebuild_catalog_rows()
    write_catalog(rows)
    print(f"ADDED\t{meta['id']}\t{dest}")
    return 0


def cmd_rebuild_catalog(_: argparse.Namespace) -> int:
    rows = rebuild_catalog_rows()
    write_catalog(rows)
    print(f"WROTE\t{CATALOG}\tcount={len(rows)}")
    return 0


def cmd_merge_pdf(args: argparse.Namespace) -> int:
    inputs = [Path(p).expanduser() for p in args.inputs]
    if args.slug:
        out = pdf_abspath(args.slug)
    elif args.output:
        out = Path(args.output).expanduser()
        if not out.is_absolute():
            out = ROOT / out
    else:
        print("need --slug Title_Slug  or  -o pdfs/Title_Slug.pdf", file=sys.stderr)
        return 2
    for p in inputs:
        if not p.is_file():
            print(f"NO_PDF\t{p}", file=sys.stderr)
            return 2
    try:
        from pypdf import PdfWriter, PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfWriter, PdfReader  # type: ignore
        except ImportError:
            print(
                "NEED_PYPDF\tpip install pypdf  (or merge externally then copy to pdfs/<Title_Slug>.pdf)",
                file=sys.stderr,
            )
            return 2
    writer = PdfWriter()
    for p in inputs:
        reader = PdfReader(str(p))
        for page in reader.pages:
            writer.add_page(page)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as f:
        writer.write(f)
    print(f"MERGED\t{out}\tparts={len(inputs)}")
    return 0


def _bib_escape(s: str) -> str:
    return s.replace("{", "\\{").replace("}", "\\}")


def cmd_export_bib(_: argparse.Namespace) -> int:
    lines = ["% Auto-exported by tools/ref_catalog.py — edit meta.yaml as source of truth.\n"]
    for d, meta in iter_papers():
        if not meta or meta.get("_error"):
            continue
        key = meta.get("cite_key") or slugify(str(meta.get("title") or d.name))[:40]
        authors = " and ".join(meta.get("authors") or ["Unknown"])
        year = str(meta.get("published_at") or "")[:4] or "n.d."
        title = _bib_escape(str(meta.get("title") or d.name))
        venue = _bib_escape(str(meta.get("venue") or ""))
        doi = meta.get("doi")
        lines.append(f"@article{{{key},")
        lines.append(f"  title = {{{title}}},")
        lines.append(f"  author = {{{_bib_escape(authors)}}},")
        lines.append(f"  year = {{{year}}},")
        if venue:
            lines.append(f"  journal = {{{venue}}},")
        if doi:
            lines.append(f"  doi = {{{doi}}},")
        lines.append(f"  note = {{ref:{meta.get('id', d.name)}}}")
        lines.append("}\n")
    BIB.parent.mkdir(parents=True, exist_ok=True)
    BIB.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"WROTE\t{BIB}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("slug")
    p.add_argument("title")
    p.set_defaults(func=cmd_slug)

    sub.add_parser("list").set_defaults(func=cmd_list)

    p = sub.add_parser("search")
    p.add_argument("query")
    p.set_defaults(func=cmd_search)

    sub.add_parser("validate").set_defaults(func=cmd_validate)
    sub.add_parser("rebuild-catalog").set_defaults(func=cmd_rebuild_catalog)
    sub.add_parser("export-bib").set_defaults(func=cmd_export_bib)

    p = sub.add_parser("add")
    p.add_argument("--title", required=True)
    p.add_argument("--slug", default=None)
    p.add_argument("--id", default=None)
    p.add_argument("--kind", default="algorithm", choices=sorted(KINDS))
    p.add_argument("--authors", default="", help="semicolon-separated")
    p.add_argument("--venue", default="")
    p.add_argument("--published-at", dest="published_at", default="")
    p.add_argument("--directions", default="", help="semicolon-separated")
    p.add_argument("--methods", default="", help="semicolon-separated")
    p.add_argument("--problem", default="")
    p.add_argument("--contribution", default="")
    p.add_argument("--doi", default=None)
    p.add_argument("--url", default=None)
    p.add_argument("--cite-key", dest="cite_key", default="")
    p.add_argument("--tags", default="")
    p.add_argument("--pdf", default=None, help="copy into pdfs/<Title_Slug>.pdf")
    p.add_argument("--appendix-merged", dest="appendix_merged", action="store_true", default=True)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("merge-pdf")
    p.add_argument("inputs", nargs="+")
    p.add_argument("--slug", default=None, help="write pdfs/<Title_Slug>.pdf")
    p.add_argument("-o", "--output", default=None, help="explicit output path")
    p.set_defaults(func=cmd_merge_pdf)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
