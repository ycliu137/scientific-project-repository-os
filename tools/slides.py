#!/usr/bin/env python3
"""External Beamer slides: init / snapshot / compile / import-template.

No permanent slides/ tree in the pipeline. Output is always a user --out
directory (or a standalone talk dir with slides.yaml).

Examples:
  python3 tools/slides.py templates
  python3 tools/slides.py init --out ~/Slides/SPFID_20260908 --template clean_academic \\
      --title "SPFID progress" --author "Yu-Chen Liu"
  python3 tools/slides.py snapshot --pdf tex_docs/labs/demo.pdf --pages 1 \\
      --out ~/Slides/SPFID_20260908/figures/demo_p1.png
  python3 tools/slides.py compile --dir ~/Slides/SPFID_20260908
  python3 tools/slides.py import-template --from /path/to/deck --name my_theme
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "tools" / "slides_templates"

PLACEHOLDERS = (
    "SLIDES_SHORT_TITLE",
    "SLIDES_FULL_TITLE",
    "SLIDES_SUBTITLE",
    "SLIDES_AUTHOR",
    "SLIDES_INSTITUTE",
    "SLIDES_DATE",
)

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def _load_yaml(path: Path) -> dict:
    if yaml is None:
        raise SystemExit("PyYAML required (pip install pyyaml)")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must be a mapping")
    return data


def _dump_yaml(data: dict) -> str:
    if yaml is None:
        raise SystemExit("PyYAML required (pip install pyyaml)")
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def _short_title(title: str, limit: int = 36) -> str:
    t = " ".join(title.split())
    if len(t) <= limit:
        return t
    return t[: limit - 1].rstrip() + "…"


def list_templates() -> list[str]:
    if not TEMPLATES.is_dir():
        return []
    out = []
    for p in sorted(TEMPLATES.iterdir()):
        if p.is_dir() and not p.name.startswith("_") and (p / "main.tex").is_file():
            out.append(p.name)
    return out


def resolve_pipeline_root(explicit: Path | None, talk_dir: Path | None = None) -> Path:
    if explicit is not None:
        return explicit.expanduser().resolve()
    if talk_dir is not None:
        cfg = talk_dir / "slides.yaml"
        if cfg.is_file():
            meta = _load_yaml(cfg)
            pr = meta.get("pipeline_root")
            if pr:
                return Path(str(pr)).expanduser().resolve()
    return ROOT


def templates_dir(pipeline_root: Path) -> Path:
    return pipeline_root / "tools" / "slides_templates"


def _replace_placeholders(text: str, mapping: dict[str, str]) -> str:
    for key, val in mapping.items():
        text = text.replace(key, val)
    return text


def _fill_tex_tree(dest: Path, mapping: dict[str, str]) -> None:
    for path in dest.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".tex", ".sty", ".md", ".bib"}:
            continue
        raw = path.read_text(encoding="utf-8")
        if any(p in raw for p in PLACEHOLDERS):
            path.write_text(_replace_placeholders(raw, mapping), encoding="utf-8")


def cmd_templates(_: argparse.Namespace) -> int:
    ids = list_templates()
    if not ids:
        print(f"EMPTY\t{TEMPLATES}", file=sys.stderr)
        return 2
    for name in ids:
        readme = TEMPLATES / name / "README.md"
        blurb = ""
        if readme.is_file():
            for line in readme.read_text(encoding="utf-8").splitlines():
                if line.strip() and not line.startswith("#"):
                    blurb = line.strip()
                    break
        print(f"{name}\t{blurb}")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    out = Path(args.out).expanduser().resolve()
    pipeline = resolve_pipeline_root(
        Path(args.pipeline) if args.pipeline else None
    )
    tdir = templates_dir(pipeline) / args.template
    if not (tdir / "main.tex").is_file():
        print(f"NO_TEMPLATE\t{tdir}", file=sys.stderr)
        print("Available:", ", ".join(list_templates()) or "(none)", file=sys.stderr)
        return 2
    if out.exists() and any(out.iterdir()) and not args.force:
        print(f"EXISTS\t{out} (use --force to overwrite scaffold files)", file=sys.stderr)
        return 2

    out.mkdir(parents=True, exist_ok=True)
    # Copy template tree (skip README overwrite if present unless force)
    for src in tdir.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(tdir)
        dest = out / rel
        if dest.exists() and not args.force:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

    (out / "figures").mkdir(exist_ok=True)
    raw = out / "figures" / "_raw"
    raw.mkdir(exist_ok=True)
    (raw / ".gitkeep").write_text("", encoding="utf-8")

    title = args.title or "Untitled talk"
    mapping = {
        "SLIDES_SHORT_TITLE": args.short_title or _short_title(title),
        "SLIDES_FULL_TITLE": title,
        "SLIDES_SUBTITLE": args.subtitle or ("Journal Club" if args.template == "journal_club" else "Progress talk"),
        "SLIDES_AUTHOR": args.author or "Yu-Chen Liu",
        "SLIDES_INSTITUTE": args.institute or "UMass Chan Medical School",
        "SLIDES_DATE": args.date or date.today().isoformat(),
    }
    _fill_tex_tree(out, mapping)

    sections = {
        "clean_academic": ["background", "progress", "results", "outlook"],
        "journal_club": ["problem", "method", "results", "closing"],
        "minimal": ["content"],
    }.get(args.template, ["background", "progress", "results", "outlook"])

    meta = {
        "title": mapping["SLIDES_FULL_TITLE"],
        "subtitle": mapping["SLIDES_SUBTITLE"],
        "author": mapping["SLIDES_AUTHOR"],
        "institute": mapping["SLIDES_INSTITUTE"],
        "date": mapping["SLIDES_DATE"],
        "template": args.template,
        "pipeline_root": str(pipeline),
        "language": args.language or "en",
        "sections": sections,
        "main": "main.tex",
        "presenter_main": "main_presenter.tex" if (out / "main_presenter.tex").is_file() else None,
    }
    (out / "slides.yaml").write_text(_dump_yaml(meta), encoding="utf-8")

    readme = out / "README.md"
    if not readme.exists() or args.force:
        readme.write_text(
            f"# {mapping['SLIDES_FULL_TITLE']}\n\n"
            f"Template: `{args.template}`\n\n"
            "## Build\n\n"
            "```bash\n"
            f"python3 {pipeline / 'tools' / 'slides.py'} compile --dir {out}\n"
            "# or: latexmk -pdf main.tex\n"
            "```\n\n"
            "Figures: put slide-ready PNGs under `figures/` "
            "(use `slides.py snapshot` for large PDFs).\n"
            "Presenter notes: compile `main_presenter.tex` if present.\n",
            encoding="utf-8",
        )

    print(f"INIT\t{out}")
    print(f"TEMPLATE\t{args.template}")
    print(f"PIPELINE\t{pipeline}")
    print("NEXT\tedit content/*.tex; snapshot figures; slides.py compile --dir", out)
    return 0


def _parse_pages(spec: str) -> list[int]:
    """Parse '1,3-5,8' into 1-based page numbers."""
    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            lo, hi = int(a), int(b)
            pages.extend(range(lo, hi + 1))
        else:
            pages.append(int(part))
    return pages


def cmd_snapshot(args: argparse.Namespace) -> int:
    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    dpi = float(args.dpi)
    zoom = dpi / 72.0

    if args.pdf:
        try:
            import fitz  # PyMuPDF
        except ImportError:
            print("NEED\tpip install pymupdf", file=sys.stderr)
            return 2
        doc = fitz.open(str(Path(args.pdf).expanduser().resolve()))
        pages = _parse_pages(args.pages) if args.pages else [1]
        mat = fitz.Matrix(zoom, zoom)
        if len(pages) == 1 and out.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            pnum = pages[0]
            if pnum < 1 or pnum > len(doc):
                print(f"BAD_PAGE\t{pnum} (doc has {len(doc)})", file=sys.stderr)
                return 2
            pix = doc[pnum - 1].get_pixmap(matrix=mat, alpha=False)
            pix.save(str(out))
            print(f"SNAPSHOT\t{out}\tpage={pnum}")
            return 0
        # Multi-page: out is a directory or stem
        dest_dir = out if out.suffix == "" or out.is_dir() else out.parent
        dest_dir.mkdir(parents=True, exist_ok=True)
        stem = out.stem if out.suffix else "page"
        for pnum in pages:
            if pnum < 1 or pnum > len(doc):
                print(f"SKIP_PAGE\t{pnum}", file=sys.stderr)
                continue
            pix = doc[pnum - 1].get_pixmap(matrix=mat, alpha=False)
            path = dest_dir / f"{stem}_p{pnum:02d}.png"
            pix.save(str(path))
            print(f"SNAPSHOT\t{path}\tpage={pnum}")
        return 0

    if args.image:
        try:
            from PIL import Image
        except ImportError:
            print("NEED\tpip install pillow", file=sys.stderr)
            return 2
        src = Path(args.image).expanduser().resolve()
        im = Image.open(src)
        max_w = int(args.max_width)
        if im.width > max_w:
            ratio = max_w / float(im.width)
            im = im.resize((max_w, int(im.height * ratio)), Image.Resampling.LANCZOS)
        if out.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            out = out.with_suffix(".png")
        im.save(out)
        print(f"SNAPSHOT\t{out}\tsize={im.size}")
        return 0

    print("NEED\t--pdf or --image", file=sys.stderr)
    return 2


def cmd_compile(args: argparse.Namespace) -> int:
    talk = Path(args.dir).expanduser().resolve()
    if not talk.is_dir():
        print(f"NO_DIR\t{talk}", file=sys.stderr)
        return 2
    meta_path = talk / "slides.yaml"
    language = "en"
    main = args.main or "main.tex"
    if meta_path.is_file():
        meta = _load_yaml(meta_path)
        language = str(meta.get("language") or "en")
        if args.presenter and meta.get("presenter_main"):
            main = str(meta["presenter_main"])
        elif not args.main and meta.get("main"):
            main = str(meta["main"])

    main_path = talk / main
    if not main_path.is_file():
        print(f"NO_MAIN\t{main_path}", file=sys.stderr)
        return 2

    if language.startswith("zh") or language.lower() in {"cjk", "chinese"}:
        engine = ["latexmk", "-xelatex", "-interaction=nonstopmode", main]
    else:
        engine = ["latexmk", "-pdf", "-interaction=nonstopmode", main]

    print(f"COMPILE\t{' '.join(engine)}\tcwd={talk}")
    try:
        proc = subprocess.run(engine, cwd=talk, check=False)
    except FileNotFoundError:
        print("NEED\tlatexmk (TeX Live / MacTeX)", file=sys.stderr)
        return 2
    if proc.returncode != 0:
        print(f"FAIL\texit={proc.returncode}", file=sys.stderr)
        log = talk / Path(main).with_suffix(".log").name
        if log.is_file():
            print(f"LOG\t{log}")
        return proc.returncode

    pdf = talk / Path(main).with_suffix(".pdf").name
    print(f"OK\t{pdf}")
    return 0


def cmd_qa(args: argparse.Namespace) -> int:
    """Scan latex log for Overfull; optional PDF border scan."""
    talk = Path(args.dir).expanduser().resolve()
    log = talk / "main.log"
    if args.main:
        log = talk / Path(args.main).with_suffix(".log").name
    rc = 0
    if log.is_file():
        text = log.read_text(encoding="utf-8", errors="replace")
        overs = [ln for ln in text.splitlines() if "Overfull" in ln]
        if overs:
            rc = 1
            for ln in overs[:40]:
                print(f"OVERFULL\t{ln}")
            if len(overs) > 40:
                print(f"OVERFULL\t... {len(overs) - 40} more")
        else:
            print("LOG_OK\tno Overfull")
    else:
        print(f"NO_LOG\t{log}", file=sys.stderr)
        rc = 2

    if args.border:
        try:
            import fitz
            import numpy as np
            from PIL import Image
        except ImportError:
            print("NEED\tpymupdf pillow numpy for --border", file=sys.stderr)
            return max(rc, 2)
        pdf_path = talk / "main.pdf"
        if args.main:
            pdf_path = talk / Path(args.main).with_suffix(".pdf").name
        if not pdf_path.is_file():
            print(f"NO_PDF\t{pdf_path}", file=sys.stderr)
            return max(rc, 2)
        doc = fitz.open(str(pdf_path))
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            arr = np.asarray(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
            h, w = arr.shape[:2]
            right = arr[int(0.12 * h) : int(0.90 * h), int(0.992 * w) :].min()
            bot = arr[int(0.962 * h) : int(0.992 * h), int(0.10 * w) : int(0.95 * w)].min()
            if right < 240 or bot < 240:
                print(f"OVERFLOW\tpage={i + 1}\tR={right}\tB={bot}")
                rc = 1
        if rc == 0:
            print("BORDER_OK")
    return rc


def cmd_import_template(args: argparse.Namespace) -> int:
    src = Path(args.from_path).expanduser().resolve()
    name = re.sub(r"[^\w\-]+", "_", args.name.strip()) or "imported"
    dest = TEMPLATES / name
    if not src.is_dir():
        print(f"NO_SRC\t{src}", file=sys.stderr)
        return 2
    if dest.exists() and not args.force:
        print(f"EXISTS\t{dest}", file=sys.stderr)
        return 2
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    # Prefer copying theme + main + content if present; else whole tree
    copied = 0
    for rel in ("main.tex", "main_presenter.tex", ".latexmkrc", "theme", "content", "figures"):
        p = src / rel
        if not p.exists():
            continue
        target = dest / rel
        if p.is_dir():
            shutil.copytree(p, target, dirs_exist_ok=True)
        else:
            shutil.copy2(p, target)
        copied += 1
    if copied == 0:
        shutil.copytree(src, dest, dirs_exist_ok=True)
    (dest / "README.md").write_text(
        f"# {name}\n\nImported from `{src}`.\n",
        encoding="utf-8",
    )
    if not (dest / "main.tex").is_file():
        print(f"WARN\tno main.tex under {dest}", file=sys.stderr)
    print(f"IMPORT\t{dest}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("templates", help="List shipped templates")
    t.set_defaults(func=cmd_templates)

    i = sub.add_parser("init", help="Scaffold a talk directory from a template")
    i.add_argument("--out", required=True, help="Output talk directory (usually external)")
    i.add_argument("--template", default="clean_academic")
    i.add_argument("--pipeline", default=None, help="Pipeline/OS root (default: this repo)")
    i.add_argument("--title", default=None)
    i.add_argument("--short-title", dest="short_title", default=None)
    i.add_argument("--subtitle", default=None)
    i.add_argument("--author", default=None)
    i.add_argument("--institute", default=None)
    i.add_argument("--date", default=None)
    i.add_argument("--language", default="en", choices=["en", "zh"])
    i.add_argument("--force", action="store_true")
    i.set_defaults(func=cmd_init)

    s = sub.add_parser("snapshot", help="Rasterize PDF page(s) or downscale an image")
    s.add_argument("--pdf", default=None)
    s.add_argument("--image", default=None)
    s.add_argument("--pages", default="1", help="1-based pages, e.g. 1,3-5")
    s.add_argument("--out", required=True, help="Output PNG path or directory")
    s.add_argument("--dpi", type=float, default=144.0)
    s.add_argument("--max-width", type=int, default=1600)
    s.set_defaults(func=cmd_snapshot)

    c = sub.add_parser("compile", help="latexmk in the talk directory")
    c.add_argument("--dir", required=True)
    c.add_argument("--main", default=None)
    c.add_argument("--presenter", action="store_true", help="Use main_presenter.tex if configured")
    c.set_defaults(func=cmd_compile)

    q = sub.add_parser("qa", help="Check Overfull log (+ optional PDF border scan)")
    q.add_argument("--dir", required=True)
    q.add_argument("--main", default=None)
    q.add_argument("--border", action="store_true")
    q.set_defaults(func=cmd_qa)

    im = sub.add_parser("import-template", help="Copy a personal deck theme into slides_templates/")
    im.add_argument("--from", dest="from_path", required=True)
    im.add_argument("--name", required=True)
    im.add_argument("--force", action="store_true")
    im.set_defaults(func=cmd_import_template)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
