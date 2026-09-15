#!/usr/bin/env python3
"""Instantiate, overlay, or upgrade this OS into sibling git repos.

Modes (name collisions):

  default / --overlay   First apply onto an existing tree: NEVER overwrite a
                        file that already exists — only add missing kernel files.
  --upgrade             Refresh OS kernel into an instance. Never overwrite
                        KEEP_ON_UPGRADE. Never overwrite a kernel file the
                        instance has modified (tracked via OS_APPLIED.yaml);
                        those are listed in OS_ABSORB.md for the agent to
                        merge template improvements into the instance copy.
  --dry-run             Print planned actions without writing.

Examples:
  python3 tools/apply_to_repo.py --layout siblings --parent ~/Proj/foo --name foo
  python3 tools/apply_to_repo.py --target /existing --name foo --pack pipeline --overlay
  python3 tools/apply_to_repo.py --target . --upgrade --dry-run
  python3 tools/apply_to_repo.py --target . --upgrade
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
OS_VERSION = "0.7.2"

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
    "skills/task-ledger.md",
    "skills/project-comprehension.md",
    "skills/autoresearch.md",
    "skills/experiment-loop.md",
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
    "skills/compute-hosts.md",
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
    "tools/experiment.py",
    "tools/ref_catalog.py",
    "tools/lab.py",
    "tools/slides.py",
    "docs/change_reports/schema.yaml",
    "docs/OBJECT_SCHEMA.md",
    "docs/change_reports/_TEMPLATE.yaml",
    "workspace/current/NEXT_ACTION.yaml",
    "workspace/current/TASK_LEDGER.yaml",
    "workspace/current/COMPREHENSION.md",
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
    "docs/design/AUTORESEARCH.md",
    "docs/design/APPLY_AND_UPGRADE.md",
    "tests/test_experiment_tool.py",
]

# Directory trees copied wholesale for pipeline packs (not listed file-by-file).
PIPELINE_TREES = [
    "tools/slides_templates",
]

# Instance-owned state: ship on first instantiate, never clobber on --upgrade.
# Kernel files that the *instance modified* are also never overwritten — see
# docs/design/APPLY_AND_UPGRADE.md (hash manifest + absorb report).
KEEP_ON_UPGRADE = {
    "docs/MASTER_PLAN.md",
    "docs/NOTATION.md",
    "workspace/current/NEXT_ACTION.yaml",
    "workspace/current/TASK_LEDGER.yaml",
    "workspace/current/COMPREHENSION.md",
}

# Written by apply_to_repo (not shipped as content from the template kernel list).
MANIFEST_REL = "workspace/current/OS_APPLIED.yaml"
ABSORB_REL = "workspace/current/OS_ABSORB.md"

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



def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load_manifest(target: Path) -> dict:
    path = target / MANIFEST_REL
    if not path.is_file():
        return {"os_version": None, "files": {}}
    try:
        import yaml
    except ImportError:
        return {"os_version": None, "files": {}}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    files = data.get("files") or {}
    if not isinstance(files, dict):
        files = {}
    return {"os_version": (data.get("os_version") or None), "files": dict(files)}


def _write_manifest(target: Path, files: dict[str, str], *, previous_version: str | None) -> None:
    try:
        import yaml
    except ImportError:
        # Minimal YAML without PyYAML.
        lines = [
            f'os_version: "{OS_VERSION}"',
            f'applied_at: "{datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}"',
            f'previous_os_version: "{previous_version or ""}"',
            "files:",
        ]
        for rel in sorted(files):
            lines.append(f'  "{rel}": "{files[rel]}"')
        text = "\n".join(lines) + "\n"
    else:
        payload = {
            "os_version": OS_VERSION,
            "applied_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "previous_os_version": previous_version,
            "files": {k: files[k] for k in sorted(files)},
        }
        text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    dest = target / MANIFEST_REL
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")


def _write_absorb_report(
    target: Path,
    *,
    absorb: list[dict],
    refreshed: list[str],
    copied: list[str],
    kept: list[str],
    dry_run: bool,
) -> None:
    """Guide agents to merge template improvements into instance-modified files."""
    lines = [
        "# OS_ABSORB — pending template → instance merges",
        "",
        "Generated by `tools/apply_to_repo.py --upgrade`.",
        f"template_os_version: {OS_VERSION}",
        f"generated_at: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"dry_run: {dry_run}",
        "",
        "## Rule",
        "",
        "Kernel files the **instance modified** were **not** overwritten.",
        "Both sides' changes must be preserved: absorb template improvements",
        "into the instance file; do not discard instance-specific edits.",
        "",
        "## Agent checklist (when absorb_needed is non-empty)",
        "",
        "1. Read each path below and the matching file in the template checkout",
        "   (the `scientific-project-repository-os` you ran apply from).",
        "2. Merge **template additions/fixes** into the **instance** file.",
        "3. Keep instance science, ledger rules, and project-specific wording.",
        "4. After each successful merge, update `OS_APPLIED.yaml` hash for that",
        "   path: `python3 tools/apply_to_repo.py --target . --record-hashes`",
        "   (or re-run `--upgrade` once the file matches an intentional merge).",
        "5. Clear or shrink this report when `absorb_needed` is empty; run",
        "   `python3 tools/check_project.py`.",
        "",
        f"## absorb_needed ({len(absorb)})",
        "",
    ]
    if not absorb:
        lines.append("_None — instance kernel files are either fresh or unchanged._")
        lines.append("")
    else:
        for item in absorb:
            lines.append(f"- `{item['path']}`")
            lines.append(f"  - reason: {item['reason']}")
            lines.append(f"  - template: `{item.get('template_src', item['path'])}`")
            lines.append("")
    lines.extend(["", f"## refreshed_from_template ({len(refreshed)})", ""])
    lines.extend([f"- `{p}`" for p in refreshed] if refreshed else ["_None_"])
    lines.extend(["", f"## newly_copied ({len(copied)})", ""])
    lines.extend([f"- `{p}`" for p in copied] if copied else ["_None_"])
    lines.extend(["", f"## kept ({len(kept)})", ""])
    if kept:
        lines.extend([f"- `{p}`" for p in kept[:50]])
        if len(kept) > 50:
            lines.append("- …")
    else:
        lines.append("_None_")
    lines.append("")
    dest = target / ABSORB_REL
    if dry_run:
        print(f"ABSORB_REPORT\t(dry-run would write {ABSORB_REL}; {len(absorb)} absorb_needed)")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(lines), encoding="utf-8")
    print(f"write\t{ABSORB_REL}\tabsorb_needed={len(absorb)}")


def _decide_upgrade_action(
    *,
    dest_exists: bool,
    dest_hash: str | None,
    template_hash: str,
    last_hash: str | None,
    force_keep: bool,
) -> str:
    """Return copy|keep_state|keep|refresh|absorb|synced."""
    if force_keep:
        return "keep_state"
    if not dest_exists:
        return "copy"
    assert dest_hash is not None
    if last_hash is None:
        # No prior apply record: identical to current template → synced;
        # otherwise treat as instance-owned until absorbed.
        if dest_hash == template_hash:
            return "synced"
        return "absorb"
    if dest_hash == last_hash:
        if template_hash == last_hash:
            return "keep"  # already at last applied (= current template)
        return "refresh"  # instance untouched; template moved
    # Instance changed since last apply
    if template_hash == last_hash:
        return "keep"  # only instance changed; nothing new from template
    return "absorb"  # both changed


def _apply_shipped_file(
    *,
    target: Path,
    rel: str,
    src: Path,
    upgrade: bool,
    dry_run: bool,
    manifest_files: dict[str, str],
    new_manifest: dict[str, str],
    absorb: list[dict],
    refreshed: list[str],
    copied_list: list[str],
    kept_list: list[str],
    counters: dict[str, int],
    template_src_label: str | None = None,
) -> None:
    dest = target / rel
    template_hash = _sha256_file(src)
    force_keep = rel in KEEP_ON_UPGRADE
    dest_exists = dest.is_file()
    dest_hash = _sha256_file(dest) if dest_exists else None
    last_hash = manifest_files.get(rel)

    if not upgrade:
        if dest_exists:
            print(f"keep\t{rel}")
            counters["skipped"] += 1
            kept_list.append(rel)
            if dest_hash:
                new_manifest[rel] = dest_hash
            return
        print(f"copy\t{rel}")
        counters["copied"] += 1
        copied_list.append(rel)
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            if dest.suffix == ".sh":
                dest.chmod(dest.stat().st_mode | 0o111)
        new_manifest[rel] = template_hash
        return

    action = _decide_upgrade_action(
        dest_exists=dest_exists,
        dest_hash=dest_hash,
        template_hash=template_hash,
        last_hash=last_hash,
        force_keep=force_keep,
    )
    label = template_src_label or rel
    if action == "copy":
        print(f"copy\t{rel}")
        counters["copied"] += 1
        copied_list.append(rel)
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            if dest.suffix == ".sh":
                dest.chmod(dest.stat().st_mode | 0o111)
        new_manifest[rel] = template_hash
    elif action == "refresh":
        print(f"refresh\t{rel}")
        counters["refreshed"] += 1
        refreshed.append(rel)
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            if dest.suffix == ".sh":
                dest.chmod(dest.stat().st_mode | 0o111)
        new_manifest[rel] = template_hash
    elif action == "synced":
        print(f"synced\t{rel}")
        counters["skipped"] += 1
        kept_list.append(rel)
        new_manifest[rel] = template_hash
    elif action == "absorb":
        reason = (
            "no OS_APPLIED record and instance differs from current template"
            if last_hash is None
            else "instance and template both changed since last apply"
        )
        print(f"absorb\t{rel}\t({reason})")
        counters["absorb"] += 1
        kept_list.append(rel)
        absorb.append({"path": rel, "reason": reason, "template_src": label})
        if dest_hash:
            new_manifest[rel] = dest_hash  # keep tracking instance bytes
    else:  # keep / keep_state
        tag = "keep_state" if action == "keep_state" else "keep"
        print(f"{tag}\t{rel}")
        counters["skipped"] += 1
        kept_list.append(rel)
        if dest_hash:
            new_manifest[rel] = dest_hash


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
    dry_run: bool = False,
    record_hashes_only: bool = False,
) -> int:
    if pack == "code":
        pack = "pipeline"
    target = target.expanduser().resolve()
    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)

    if record_hashes_only:
        return _record_hashes(target, pack=pack, thin=thin)

    preexisting = {
        "os.yaml": (target / "os.yaml").is_file(),
        "SKILL.md": (target / "SKILL.md").is_file(),
        "MAP.md": (target / "MAP.md").is_file(),
        "AGENTS.md": (target / "AGENTS.md").is_file(),
        "README.md": (target / "README.md").is_file(),
    }
    mode = "upgrade" if upgrade else ("overlay" if overlay or preexisting["os.yaml"] or preexisting["SKILL.md"] else "instantiate")
    print(f"MODE\t{mode}\tpack={pack}\tstrictness={strictness}\tdry_run={dry_run}")

    manifest = _load_manifest(target)
    manifest_files: dict[str, str] = dict(manifest.get("files") or {})
    new_manifest: dict[str, str] = dict(manifest_files)
    absorb: list[dict] = []
    refreshed: list[str] = []
    copied_list: list[str] = []
    kept_list: list[str] = []
    counters = {"copied": 0, "skipped": 0, "refreshed": 0, "absorb": 0}

    files = list(KERNEL_FILES)
    if pack == "pipeline" and not thin:
        files.extend(PIPELINE_EXTRA)
    if pack == "source":
        files.extend(SOURCE_EXTRA)

    # Pack overlays own these dest paths (e.g. source SKILL.md). Do not also
    # ship the pipeline kernel constitution into that path on upgrade.
    pack_overlay_dests = {dest for _src, dest in PACK_OVERLAY.get(pack, [])}
    files = [rel for rel in files if rel not in pack_overlay_dests]

    for rel in files:
        src = SOURCE / rel
        if not src.is_file():
            print(f"MISSING_IN_TEMPLATE\t{rel}", file=sys.stderr)
            continue
        _apply_shipped_file(
            target=target,
            rel=rel,
            src=src,
            upgrade=upgrade,
            dry_run=dry_run,
            manifest_files=manifest_files,
            new_manifest=new_manifest,
            absorb=absorb,
            refreshed=refreshed,
            copied_list=copied_list,
            kept_list=kept_list,
            counters=counters,
        )

    if pack == "pipeline" and not thin:
        for tree_rel in PIPELINE_TREES:
            src_root = SOURCE / tree_rel
            if not src_root.is_dir():
                print(f"MISSING_IN_TEMPLATE\t{tree_rel}/", file=sys.stderr)
                continue
            dest_root = target / tree_rel
            if not dest_root.exists() and not upgrade:
                print(f"copytree\t{tree_rel}/")
                counters["copied"] += 1
                copied_list.append(tree_rel + "/")
                if not dry_run:
                    shutil.copytree(src_root, dest_root)
                for p in sorted(src_root.rglob("*")):
                    if p.is_file():
                        rel = str(p.relative_to(SOURCE))
                        new_manifest[rel] = _sha256_file(p)
                continue
            # Per-file decisions inside the tree
            for p in sorted(src_root.rglob("*")):
                if not p.is_file():
                    continue
                rel = str(p.relative_to(SOURCE))
                _apply_shipped_file(
                    target=target,
                    rel=rel,
                    src=p,
                    upgrade=upgrade,
                    dry_run=dry_run,
                    manifest_files=manifest_files,
                    new_manifest=new_manifest,
                    absorb=absorb,
                    refreshed=refreshed,
                    copied_list=copied_list,
                    kept_list=kept_list,
                    counters=counters,
                )

    for src_rel, dest_rel in PACK_OVERLAY.get(pack, []):
        src = SOURCE / src_rel
        if not src.is_file():
            print(
                f"ERROR\tpack overlay missing {src_rel} — run apply from the "
                "template repo or the pipeline instance (which ships packs/)",
                file=sys.stderr,
            )
            return 2
        if not upgrade and preexisting.get(dest_rel):
            print(f"keep\t{dest_rel}")
            counters["skipped"] += 1
            kept_list.append(dest_rel)
            continue
        _apply_shipped_file(
            target=target,
            rel=dest_rel,
            src=src,
            upgrade=upgrade,
            dry_run=dry_run,
            manifest_files=manifest_files,
            new_manifest=new_manifest,
            absorb=absorb,
            refreshed=refreshed,
            copied_list=copied_list,
            kept_list=kept_list,
            counters=counters,
            template_src_label=src_rel,
        )

    _write_absorb_report(
        target,
        absorb=absorb,
        refreshed=refreshed,
        copied=copied_list,
        kept=kept_list,
        dry_run=dry_run,
    )

    if dry_run:
        print(
            f"SUMMARY\tdry_run copy={counters['copied']} keep={counters['skipped']} "
            f"refresh={counters['refreshed']} absorb={counters['absorb']} (no writes)"
        )
        print(
            "HINT\tInstance-modified kernel files are never overwritten; see absorb list."
        )
        return 0

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
        counters["skipped"] += 1
    elif preexisting["os.yaml"] and upgrade:
        try:
            import yaml  # local optional
        except ImportError:
            yaml = None
        if yaml is None:
            print("WARN\tcannot merge os.yaml (PyYAML missing)", file=sys.stderr)
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
        counters["copied"] += 1

    gi = target / ".gitignore"
    if not gi.exists():
        gi.write_text(_gitignore_for(pack), encoding="utf-8")
        print("write\t.gitignore")
        counters["copied"] += 1
    elif upgrade:
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
            counters["skipped"] += 1
    else:
        print("keep\t.gitignore")
        counters["skipped"] += 1

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
            body = (
                f"# {name} (pipeline)\n\n"
                "Default AI entry. See `SKILL.md`, `MAP.md`, `COLD_START.md`.\n"
            )
        readme.write_text(body, encoding="utf-8")
        print("write\tREADME.md")
        counters["copied"] += 1
    else:
        print("keep\tREADME.md")
        counters["skipped"] += 1

    _write_manifest(target, new_manifest, previous_version=manifest.get("os_version"))
    print(f"write\t{MANIFEST_REL}")

    print(
        f"SUMMARY\tcopy={counters['copied']} keep={counters['skipped']} "
        f"refresh={counters['refreshed']} absorb={counters['absorb']}"
    )
    print(
        "HINT\tInstance-only paths (pipelines/, objects/, dat/, docs/design/* "
        "not shipped by the template, Change Reports) were not in the copy set."
    )
    if absorb:
        print(
            f"HINT\t{len(absorb)} file(s) need absorb — read {ABSORB_REL} and merge "
            "template improvements into the instance copies (do not clobber)."
        )
    return 0


def _record_hashes(target: Path, *, pack: str, thin: bool) -> int:
    """Refresh OS_APPLIED hashes from current instance bytes (after a manual absorb)."""
    files = list(KERNEL_FILES)
    if pack == "pipeline" and not thin:
        files.extend(PIPELINE_EXTRA)
    if pack == "source":
        files.extend(SOURCE_EXTRA)
    new_files: dict[str, str] = {}
    for rel in files:
        p = target / rel
        if p.is_file():
            new_files[rel] = _sha256_file(p)
    if pack == "pipeline" and not thin:
        for tree_rel in PIPELINE_TREES:
            root = target / tree_rel
            if not root.is_dir():
                continue
            for p in sorted(root.rglob("*")):
                if p.is_file():
                    rel = str(p.relative_to(target))
                    new_files[rel] = _sha256_file(p)
    for _src_rel, dest_rel in PACK_OVERLAY.get(pack, []):
        p = target / dest_rel
        if p.is_file():
            new_files[dest_rel] = _sha256_file(p)
    prev = _load_manifest(target)
    _write_manifest(target, new_files, previous_version=prev.get("os_version"))
    print(f"write\t{MANIFEST_REL}\trecorded={len(new_files)}")
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
    ap.add_argument("--overlay", action="store_true",
                    help="First apply onto existing tree (never overwrite; same as default when files exist)")
    ap.add_argument("--upgrade", action="store_true",
                    help="Refresh OS kernel; never overwrite KEEP_ON_UPGRADE or instance-modified files")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print keep/copy/refresh/absorb plan without writing")
    ap.add_argument("--record-hashes", action="store_true",
                    help="Rewrite OS_APPLIED.yaml hashes from current instance files (after absorb merge)")
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
        dry_run=args.dry_run,
        record_hashes_only=args.record_hashes,
    )


if __name__ == "__main__":
    raise SystemExit(main())
