#!/usr/bin/env python3
"""Instantiate or overlay this OS into sibling git repos.

Examples:
  python3 tools/apply_to_repo.py --layout siblings --parent ~/Proj/foo --name foo
  python3 tools/apply_to_repo.py --target /existing --name foo --pack pipeline --overlay
  python3 tools/apply_to_repo.py --target ../foo_ref --name foo_ref --pack ref \
      --sibling-pipeline ../foo_pipeline --sibling-source ../foo --sibling-data ../foo_data
  python3 tools/apply_to_repo.py --target ../foo_paper --name foo_paper --pack paper \\
      --sibling-pipeline ../foo_pipeline --sibling-source ../foo --sibling-data ../foo_data
  python3 tools/apply_to_repo.py --target . --upgrade
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
OS_VERSION = "0.6.2"

KERNEL_FILES = [
    "SKILL.md",
    "AGENTS.md",
    "MAP.md",
    "COLD_START.md",
    "requirements.txt",
    "skills/bootstrap.md",
    "skills/retrieval.md",
    "skills/adding-knowledge.md",
    "skills/change-report.md",
    "skills/reindex.md",
    "skills/consult-plan.md",
    "skills/maintenance.md",
    "skills/evolution.md",
    "skills/paper-entry.md",
    "skills/pipeline-entry.md",
    "skills/pipeline-modules.md",
    "skills/source-package.md",
    "skills/data-management.md",
    "skills/meeting-record.md",
    "skills/tex-docs.md",
    "skills/code-change.md",
    "skills/runtime-env.md",
    "skills/language.md",
    "skills/notation.md",
    "skills/reference-papers.md",
    "skills/backend-lab.md",
    "skills/slides.md",
    "skills/journal-club-slides.md",
    "tools/os_config.py",
    "tools/nav.py",
    "tools/build_nav_index.py",
    "tools/project_api.py",
    "tools/plan_pointer.py",
    "tools/bridge.py",
    "tools/code_bridge.py",
    "tools/apply_to_repo.py",
    "tools/compile_tex_docs.py",
    "tools/check_project.py",
    "tools/ref_catalog.py",
    "tools/lab.py",
    "tools/slides.py",
    "docs/change_reports/schema.yaml",
    "docs/OBJECT_SCHEMA.md",
    "docs/change_reports/_TEMPLATE.yaml",
    "workspace/current/NEXT_ACTION.yaml",
    "index/tree.yaml",
]

SOURCE_EXTRA = [
    "env/README.md",
    "env/catalog.yaml",
    "env/_TEMPLATE.sh",
    "env/specs/README.md",
]

PIPELINE_EXTRA = [
    "skills/objects/hypotheses.md",
    "skills/objects/experiments.md",
    "skills/objects/claims.md",
    "skills/objects/sources.md",
    "skills/objects/results.md",
    "skills/objects/failures.md",
    "docs/MASTER_PLAN.md",
    "docs/NOTATION.md",
    "tests/test_smoke.py",
    "tests/smoke/README.md",
    "env/README.md",
    "env/catalog.yaml",
    "env/_TEMPLATE.sh",
    "env/specs/README.md",
    "tex_docs/README.md",
    "meeting_record/README.md",
    "tools/packs/paper/SKILL.md",
    "tools/packs/paper/MAP.md",
    "tools/packs/paper/os.yaml",
    "tools/packs/paper/AGENTS.md",
    "tools/packs/source/SKILL.md",
    "tools/packs/source/MAP.md",
    "tools/packs/source/AGENTS.md",
    "tools/packs/data/SKILL.md",
    "tools/packs/data/MAP.md",
    "tools/packs/data/AGENTS.md",
    "tools/packs/ref/SKILL.md",
    "tools/packs/ref/MAP.md",
    "tools/packs/ref/AGENTS.md",
    "tools/packs/ref/papers/_TEMPLATE/meta.yaml",
    "tools/packs/ref/papers/_TEMPLATE/notes.md",
    "tools/packs/ref/pdfs/README.md",
    "backend_lab/README.md",
    "backend_lab/_TEMPLATE/LAB.yaml",
    "backend_lab/_TEMPLATE/run.py",
    "backend_lab/_TEMPLATE/notes.md",
    "docs/design/BACKEND_LAB.md",
    "docs/design/SLIDES.md",
]

# Directory trees copied wholesale for pipeline packs (not listed file-by-file).
PIPELINE_TREES = [
    "tools/slides_templates",
]

# Instance-owned stubs: ship on first instantiate, never clobber on --upgrade.
KEEP_ON_UPGRADE = {
    "docs/MASTER_PLAN.md",
    "docs/NOTATION.md",
    "workspace/current/NEXT_ACTION.yaml",
}

PACK_OVERLAY = {
    "paper": [
        ("tools/packs/paper/SKILL.md", "SKILL.md"),
        ("tools/packs/paper/MAP.md", "MAP.md"),
        ("tools/packs/paper/AGENTS.md", "AGENTS.md"),
    ],
    "source": [
        ("tools/packs/source/SKILL.md", "SKILL.md"),
        ("tools/packs/source/MAP.md", "MAP.md"),
        ("tools/packs/source/AGENTS.md", "AGENTS.md"),
    ],
    "data": [
        ("tools/packs/data/SKILL.md", "SKILL.md"),
        ("tools/packs/data/MAP.md", "MAP.md"),
        ("tools/packs/data/AGENTS.md", "AGENTS.md"),
    ],
    "ref": [
        ("tools/packs/ref/SKILL.md", "SKILL.md"),
        ("tools/packs/ref/MAP.md", "MAP.md"),
        ("tools/packs/ref/AGENTS.md", "AGENTS.md"),
    ],
}

INCLUDE = {
    "pipeline": """  - skills
  - docs
  - tex_docs
  - tools
  - workspace
  - index
  - tests
  - env
  - objects
  - pipelines""",
    "source": """  - skills
  - tools
  - src
  - tests
  - env
  - docs""",
    "data": """  - skills
  - tools
  - datasets
  - integrated
  - preprocess
  - docs""",
    "paper": """  - skills
  - docs
  - tools
  - workspace
  - index
  - tex""",
    "ref": """  - skills
  - tools
  - papers
  - bib
  - docs""",
}


def _pkg_name(slug: str) -> str:
    return slug.replace("-", "_")


def _write_os_yaml(
    dest: Path,
    *,
    name: str,
    pack: str,
    strictness: str,
    siblings: dict[str, str | None],
) -> None:
    def block(role: str) -> str:
        path = siblings.get(role)
        enabled = "true" if path else "false"
        path_s = path if path else "null"
        env = {
            "source": "SOURCE_REPO_ROOT",
            "pipeline": "PIPELINE_REPO_ROOT",
            "data": "DATA_REPO_ROOT",
            "ref": "REF_REPO_ROOT",
            "paper": "PAPER_REPO_ROOT",
        }[role]
        return (
            f"  {role}:\n"
            f"    enabled: {enabled}\n"
            f"    path: {path_s}\n"
            f"    env: {env}"
        )

    roots = INCLUDE.get(pack, INCLUDE["pipeline"])
    y = f"""# Scientific Project Repository OS — instance config
os:
  name: scientific-project-repository-os
  version: "{OS_VERSION}"
  pack: {pack}
  strictness: {strictness}

project:
  name: {name}
  slug: {name}
  kind: instance

siblings:
{block("source")}
{block("pipeline")}
{block("data")}
{block("ref")}
{block("paper")}

include_roots:
{roots}

legacy_roots: []

runtime:
  env_kind: system
  env_name: null
  python: python3
  pytest_module: true
  env_dir: env
"""
    dest.write_text(y, encoding="utf-8")


def _gitignore_for(pack: str) -> str:
    base = (SOURCE / ".gitignore").read_text(encoding="utf-8") if (SOURCE / ".gitignore").is_file() else ""
    extra = ""
    if pack == "pipeline":
        extra = (
            "\nmeeting_record/*\n!meeting_record/README.md\n"
            "tex_docs/**/*.aux\ntex_docs/**/*.log\ntex_docs/**/*.out\n"
            "tex_docs/**/*.fls\ntex_docs/**/*.fdb_latexmk\ntex_docs/**/*.synctex.gz\n"
            "# Backend lab: keep code/docs; ignore run outputs only\n"
            "backend_lab/**/outputs/\n"
            "backend_lab/**/output/\n"
            "backend_lab/**/*.npy\n"
            "backend_lab/**/*.npz\n"
            "backend_lab/**/*.h5\n"
            "backend_lab/**/*.pkl\n"
            "backend_lab/**/*.pickle\n"
            "backend_lab/**/*.pt\n"
            "backend_lab/**/*.pth\n"
            "backend_lab/**/*.ckpt\n"
            "backend_lab/**/*.log\n"
            "backend_lab/**/__pycache__/\n"
        )
    if pack == "data":
        extra += "\ndatasets/**/raw/**\n*.h5\n*.hdf5\n*.parquet\n*.bam\n*.fastq.gz\n"
    if pack == "ref":
        extra += (
            "\n# Reference PDFs — local only (do not commit; use title-slug names)\n"
            "pdfs/*.pdf\n"
            "!pdfs/README.md\n"
        )
    return base + extra


def _write_source_package(target: Path, slug: str) -> None:
    pkg = _pkg_name(slug)
    src = target / "src" / pkg
    src.mkdir(parents=True, exist_ok=True)
    init = src / "__init__.py"
    if not init.exists():
        init.write_text(f'"""Installable package ({pkg}). Keep this repo independently runnable."""\n\n__version__ = "0.0.1"\n', encoding="utf-8")
    tests = target / "tests"
    tests.mkdir(parents=True, exist_ok=True)
    smoke = tests / "test_smoke.py"
    if not smoke.exists():
        smoke.write_text(
            f'''"""Source package must import without pipeline or data."""\n\nimport {pkg}\n\n\ndef test_import():\n    assert {pkg}.__version__\n''',
            encoding="utf-8",
        )
    pyproject = target / "pyproject.toml"
    if not pyproject.exists():
        pyproject.write_text(
            f'''[build-system]\nrequires = ["setuptools>=61"]\nbuild-backend = "setuptools.build_meta"\n\n[project]\nname = "{pkg}"\nversion = "0.0.1"\ndescription = "Publicable source package (edit from the pipeline sibling)."\nreadme = "README.md"\nrequires-python = ">=3.10"\n\n[tool.setuptools.packages.find]\nwhere = ["src"]\n''',
            encoding="utf-8",
        )
    env_src = SOURCE / "env"
    dest_env = target / "env"
    if env_src.is_dir():
        for rel in ("README.md", "catalog.yaml", "_TEMPLATE.sh", "specs/README.md"):
            s = env_src / rel
            d = dest_env / rel
            if s.is_file() and not d.exists():
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(s, d)
                if d.suffix == ".sh":
                    d.chmod(d.stat().st_mode | 0o111)


def _write_data_layout(target: Path) -> None:
    for d in (
        target / "datasets" / "_TEMPLATE",
        target / "integrated" / "_TEMPLATE",
        target / "preprocess",
    ):
        d.mkdir(parents=True, exist_ok=True)
    meta = target / "datasets" / "_TEMPLATE" / "meta.yaml"
    if not meta.exists():
        meta.write_text(
            """id: DATASET_ID
title: ""
accessed_at: YYYY-MM-DD
license: ""
source_url: ""
source_paper: ""
source_paper_id: null   # optional S_* in the pipeline repo
raw_dir: raw/
processed_dir: processed/
notes: >
  Copy this folder to datasets/<id>/. Keep raw original. Write processed for pipeline/source.
""",
            encoding="utf-8",
        )
    catalog = target / "catalog.yaml"
    if not catalog.exists():
        catalog.write_text(
            """# Dataset index (adapt per project — see skills/data-management.md)
datasets: []
integrated: []
""",
            encoding="utf-8",
        )
    (target / "datasets" / "_TEMPLATE" / "raw").mkdir(exist_ok=True)
    (target / "datasets" / "_TEMPLATE" / "processed").mkdir(exist_ok=True)
    (target / "preprocess" / "README.md").write_text(
        "# Preprocess\n\nScripts that turn `datasets/<id>/raw` into `processed`. May import the source package. Must not import pipeline.\n",
        encoding="utf-8",
    ) if not (target / "preprocess" / "README.md").exists() else None


def _write_ref_layout(target: Path) -> None:
    papers = target / "papers" / "_TEMPLATE"
    papers.mkdir(parents=True, exist_ok=True)
    pdfs = target / "pdfs"
    pdfs.mkdir(parents=True, exist_ok=True)
    (target / "bib").mkdir(parents=True, exist_ok=True)
    src_pack = SOURCE / "tools" / "packs" / "ref"
    for name in ("meta.yaml", "notes.md"):
        s = src_pack / "papers" / "_TEMPLATE" / name
        d = papers / name
        if s.is_file() and not d.exists():
            d.write_text(s.read_text(encoding="utf-8"), encoding="utf-8")
    pdf_readme_src = src_pack / "pdfs" / "README.md"
    pdf_readme = pdfs / "README.md"
    if pdf_readme_src.is_file():
        pdf_readme.write_text(pdf_readme_src.read_text(encoding="utf-8"), encoding="utf-8")
    elif not pdf_readme.exists():
        pdf_readme.write_text(
            "# PDFs (local only)\n\nStore `pdfs/<Title_Slug>.pdf` here. Gitignored.\n",
            encoding="utf-8",
        )
    catalog = target / "catalog.yaml"
    if not catalog.exists():
        catalog.write_text(
            """# Reference paper index (see skills/reference-papers.md)
papers: []
""",
            encoding="utf-8",
        )
    bib = target / "bib" / "references.bib"
    if not bib.exists():
        bib.write_text("% Export with: python3 tools/ref_catalog.py export-bib\n", encoding="utf-8")
    readme = target / "papers" / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Papers\n\n"
            "One folder per article title slug (`meta.yaml` + optional `notes.md`).\n"
            "PDFs live in `../pdfs/<Title_Slug>.pdf` (gitignored). See `skills/reference-papers.md`.\n",
            encoding="utf-8",
        )



def apply(
    target: Path,
    *,
    name: str,
    pack: str,
    overlay: bool,
    upgrade: bool,
    strictness: str,
    siblings: dict[str, str | None],
    thin: bool,
) -> int:
    if pack == "code":
        pack = "pipeline"
    target = target.expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    preexisting = {
        "os.yaml": (target / "os.yaml").is_file(),
        "SKILL.md": (target / "SKILL.md").is_file(),
        "MAP.md": (target / "MAP.md").is_file(),
        "AGENTS.md": (target / "AGENTS.md").is_file(),
        "README.md": (target / "README.md").is_file(),
    }
    print(f"MODE\t{'overlay' if overlay else 'instantiate'}\tpack={pack}\tstrictness={strictness}")

    files = list(KERNEL_FILES)
    if pack == "pipeline" and not thin:
        files.extend(PIPELINE_EXTRA)
    if pack == "source":
        files.extend(SOURCE_EXTRA)

    copied = 0
    skipped = 0
    for rel in files:
        src = SOURCE / rel
        if not src.is_file():
            print(f"MISSING_IN_TEMPLATE\t{rel}", file=sys.stderr)
            continue
        dest = target / rel
        if dest.exists() and (not upgrade or rel in KEEP_ON_UPGRADE):
            print(f"keep\t{rel}")
            skipped += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        if dest.suffix == ".sh":
            dest.chmod(dest.stat().st_mode | 0o111)
        print(f"copy\t{rel}")
        copied += 1

    if pack == "pipeline" and not thin:
        for rel in PIPELINE_TREES:
            src = SOURCE / rel
            if not src.is_dir():
                print(f"MISSING_IN_TEMPLATE\t{rel}/", file=sys.stderr)
                continue
            dest = target / rel
            if dest.exists() and not upgrade:
                print(f"keep\t{rel}/")
                skipped += 1
                continue
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            print(f"copytree\t{rel}/")
            copied += 1

    for src_rel, dest_rel in PACK_OVERLAY.get(pack, []):
        src = SOURCE / src_rel
        dest = target / dest_rel
        if not src.is_file():
            print(
                f"ERROR\tpack overlay missing {src_rel} — run apply from the "
                "template repo or the pipeline instance (which ships packs/)",
                file=sys.stderr,
            )
            return 2
        if preexisting.get(dest_rel) and not upgrade:
            print(f"keep\t{dest_rel}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"pack\t{src_rel} -> {dest_rel}")
        copied += 1

    if pack == "paper":
        tex = target / "tex"
        tex.mkdir(exist_ok=True)
        (tex / ".gitkeep").write_text("", encoding="utf-8")
    if pack == "source":
        _write_source_package(target, name)
    if pack == "data":
        _write_data_layout(target)
    if pack == "ref":
        _write_ref_layout(target)

    os_path = target / "os.yaml"
    if preexisting["os.yaml"] and not upgrade:
        print("keep\tos.yaml")
    elif preexisting["os.yaml"] and upgrade:
        # Preserve siblings / runtime; only bump OS version metadata.
        try:
            import yaml  # local optional
        except ImportError:
            yaml = None
        if yaml is None:
            print("WARN\toverwrite os.yaml (PyYAML missing; cannot merge)", file=sys.stderr)
            _write_os_yaml(
                os_path,
                name=name,
                pack=pack,
                strictness=strictness,
                siblings=siblings,
            )
            print("write\tos.yaml")
        else:
            data = yaml.safe_load(os_path.read_text(encoding="utf-8")) or {}
            data.setdefault("os", {})
            data["os"]["version"] = OS_VERSION
            data["os"]["name"] = data["os"].get("name") or "scientific-project-repository-os"
            if "pack" not in data["os"]:
                data["os"]["pack"] = pack
            os_path.write_text(
                yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            print("merge\tos.yaml\tversion=" + OS_VERSION)
    else:
        _write_os_yaml(
            os_path,
            name=name,
            pack=pack,
            strictness=strictness,
            siblings=siblings,
        )
        print("write\tos.yaml")

    gi = target / ".gitignore"
    if not gi.exists():
        gi.write_text(_gitignore_for(pack), encoding="utf-8")
        print("write\t.gitignore")
    elif upgrade:
        # Append missing ignore rules without duplicating the whole file.
        desired = _gitignore_for(pack)
        cur = gi.read_text(encoding="utf-8")
        added = 0
        for line in desired.splitlines():
            if line.strip() and line not in cur:
                if not cur.endswith("\n"):
                    cur += "\n"
                cur += line + "\n"
                added += 1
        if added:
            gi.write_text(cur, encoding="utf-8")
            print(f"merge\t.gitignore\t+{added} lines")
        else:
            print("keep\t.gitignore")
    else:
        print("keep\t.gitignore")

    readme = target / "README.md"
    if not readme.exists():
        if pack == "source":
            body = (
                f"# {name}\n\nPublicable source package. "
                f"Default agent entry is the **pipeline** sibling. "
                f"`pip install -e .` then import `{_pkg_name(name)}`.\n"
            )
        elif pack == "data":
            body = f"# {name} (data)\n\nPrivate data sibling. Operate from the pipeline repo via `tools/bridge.py`.\n"
        elif pack == "paper":
            body = f"# {name} (paper)\n\nWriting entry. Agents start at `SKILL.md`.\n"
        elif pack == "ref":
            body = (
                f"# {name} (ref)\n\n"
                "Reference literature sibling. Ingest from the **pipeline** repo; "
                "cite from the **paper** repo via `bib/references.bib`. "
                "Metadata in `papers/<Title_Slug>/`; PDFs in `pdfs/<Title_Slug>.pdf` "
                "(title-slug names; PDFs gitignored).\n"
            )
        else:
            body = f"# {name} (pipeline)\n\nDefault agent entry. Agents start at `SKILL.md`.\n"
        readme.write_text(body, encoding="utf-8")
        print("write\tREADME.md")

    print(f"DONE\tcopied={copied}\tskipped={skipped}\ttarget={target}")
    print("NEXT\tcd there; python3 tools/nav.py rebuild; python3 tools/check_project.py")
    return 0


def apply_siblings(parent: Path, name: str, strictness: str) -> int:
    parent = parent.expanduser().resolve()
    parent.mkdir(parents=True, exist_ok=True)
    src = parent / name
    pipe = parent / f"{name}_pipeline"
    data = parent / f"{name}_data"
    ref = parent / f"{name}_ref"
    rel = {
        "from_source": {
            "source": None,
            "pipeline": f"../{name}_pipeline",
            "data": f"../{name}_data",
            "ref": f"../{name}_ref",
            "paper": None,
        },
        "from_pipeline": {
            "source": f"../{name}",
            "pipeline": None,
            "data": f"../{name}_data",
            "ref": f"../{name}_ref",
            "paper": None,
        },
        "from_data": {
            "source": f"../{name}",
            "pipeline": f"../{name}_pipeline",
            "data": None,
            "ref": f"../{name}_ref",
            "paper": None,
        },
        "from_ref": {
            "source": f"../{name}",
            "pipeline": f"../{name}_pipeline",
            "data": f"../{name}_data",
            "ref": None,
            "paper": None,
        },
    }
    rc = apply(src, name=name, pack="source", overlay=False, upgrade=False, strictness=strictness, siblings=rel["from_source"], thin=True)
    if rc:
        return rc
    rc = apply(pipe, name=f"{name}_pipeline", pack="pipeline", overlay=False, upgrade=False, strictness=strictness, siblings=rel["from_pipeline"], thin=False)
    if rc:
        return rc
    rc = apply(data, name=f"{name}_data", pack="data", overlay=False, upgrade=False, strictness=strictness, siblings=rel["from_data"], thin=True)
    if rc:
        return rc
    rc = apply(ref, name=f"{name}_ref", pack="ref", overlay=False, upgrade=False, strictness=strictness, siblings=rel["from_ref"], thin=True)
    print(f"LAYOUT\tparent={parent}")
    print(f"  source    {src}  (publicable package)")
    print(f"  pipeline  {pipe}  ★ default agent entry")
    print(f"  data      {data}")
    print(f"  ref       {ref}  (reference literature)")
    print(f"NEXT\tcd {pipe} && pip install -e {src} && python3 tools/nav.py rebuild")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--layout", choices=["none", "siblings"], default="none")
    ap.add_argument("--parent", default=None, help="Grouping folder for --layout siblings (not a git repo)")
    ap.add_argument("--target", default=None, help="Destination repo root (single-pack apply)")
    ap.add_argument("--name", default=None, help="project slug")
    ap.add_argument("--pack", choices=["source", "pipeline", "data", "ref", "paper", "code"], default="pipeline")
    ap.add_argument("--overlay", action="store_true")
    ap.add_argument("--upgrade", action="store_true")
    ap.add_argument("--strictness", choices=["warn", "error"], default="warn")
    ap.add_argument("--sibling", default=None, help="Deprecated: treated as --sibling-source or pipeline for paper")
    ap.add_argument("--sibling-source", default=None)
    ap.add_argument("--sibling-pipeline", default=None)
    ap.add_argument("--sibling-data", default=None)
    ap.add_argument("--sibling-paper", default=None)
    ap.add_argument("--sibling-ref", default=None)
    ap.add_argument("--thin", action="store_true")
    args = ap.parse_args()

    if args.layout == "siblings":
        if not args.parent or not args.name:
            print("--layout siblings requires --parent and --name", file=sys.stderr)
            return 2
        return apply_siblings(Path(args.parent), args.name, args.strictness)

    if not args.target:
        print("--target is required unless --layout siblings", file=sys.stderr)
        return 2
    target = Path(args.target)
    name = args.name or target.name
    pack = "pipeline" if args.pack == "code" else args.pack
    # On upgrade, prefer the instance's recorded pack unless the user overrode --pack.
    if args.upgrade and "--pack" not in sys.argv:
        os_path = target.expanduser().resolve() / "os.yaml"
        if os_path.is_file():
            try:
                import yaml
            except ImportError:
                yaml = None
            if yaml is not None:
                data = yaml.safe_load(os_path.read_text(encoding="utf-8")) or {}
                recorded = ((data.get("os") or {}).get("pack") or "").strip()
                if recorded in ("source", "pipeline", "data", "ref", "paper"):
                    pack = recorded
    siblings = {
        "source": args.sibling_source,
        "pipeline": args.sibling_pipeline,
        "data": args.sibling_data,
        "ref": args.sibling_ref,
        "paper": args.sibling_paper,
    }
    if args.sibling:
        if pack == "paper" and not siblings["pipeline"]:
            siblings["pipeline"] = args.sibling
        elif not siblings["source"]:
            siblings["source"] = args.sibling
    return apply(
        target,
        name=name,
        pack=pack,
        overlay=args.overlay,
        upgrade=args.upgrade,
        strictness=args.strictness,
        siblings=siblings,
        thin=args.thin,
    )


if __name__ == "__main__":
    raise SystemExit(main())
