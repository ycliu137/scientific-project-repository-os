#!/usr/bin/env python3
"""Load os.yaml (instance identity). Stdlib fallback if PyYAML is missing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def _simple_yaml(text: str) -> dict[str, Any]:
    """Tiny nested-map parser for this repo's os.yaml (indent = 2 spaces)."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any] | list[Any]]] = [(-1, root)]
    pending_key: tuple[dict[str, Any], str] | None = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if line.startswith("- "):
            while stack and indent < stack[-1][0]:
                stack.pop()
            item = line[2:].strip().strip("'\"")
            parent = stack[-1][1]
            if isinstance(parent, list):
                parent.append(item)
            elif pending_key is not None:
                d, k = pending_key
                lst: list[Any] = []
                d[k] = lst
                lst.append(item)
                stack.append((indent, lst))
                pending_key = None
            continue
        if ":" not in line:
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if not isinstance(parent, dict):
            continue
        if rest in ("", "|", ">"):
            pending_key = (parent, key)
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
            continue
        pending_key = None
        if rest in ("null", "Null", "~"):
            parent[key] = None
        elif rest in ("true", "True"):
            parent[key] = True
        elif rest in ("false", "False"):
            parent[key] = False
        elif rest.startswith("[") and rest.endswith("]"):
            inner = rest[1:-1].strip()
            parent[key] = [p.strip().strip("'\"") for p in inner.split(",") if p.strip()] if inner else []
        else:
            parent[key] = rest.strip("'\"")
    return root


def load_os(root: Path) -> dict[str, Any]:
    path = root / "os.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"missing {path}")
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text) or {}
    else:
        data = _simple_yaml(text)
    if not isinstance(data, dict):
        raise ValueError("os.yaml must be a mapping")
    return data


def project_slug(root: Path) -> str:
    data = load_os(root)
    slug = (data.get("project") or {}).get("slug")
    if not slug:
        raise ValueError("os.yaml project.slug is required")
    return str(slug)


def os_pack(root: Path) -> str:
    pack = str((load_os(root).get("os") or {}).get("pack") or "pipeline")
    if pack == "code":
        return "pipeline"
    return pack


def strictness(root: Path) -> str:
    return str((load_os(root).get("os") or {}).get("strictness") or "warn")


SIBLING_ORDER = ("source", "pipeline", "data", "paper")

_DEFAULT_ENV = {
    "source": "SOURCE_REPO_ROOT",
    "pipeline": "PIPELINE_REPO_ROOT",
    "data": "DATA_REPO_ROOT",
    "paper": "PAPER_REPO_ROOT",
}

_DEFAULT_SIBLING_FOR_PACK = {
    "pipeline": "source",
    "paper": "pipeline",
    "data": "source",
    "source": "pipeline",
}


def siblings_cfg(root: Path) -> dict[str, Any]:
    data = load_os(root)
    sibs = data.get("siblings")
    if isinstance(sibs, dict) and sibs:
        return sibs
    old = data.get("sibling") or {}
    if not old:
        return {}
    pack = os_pack(root)
    target = "source" if pack == "paper" else "pipeline"
    if pack == "pipeline":
        target = "source"
    return {target: old}


def _resolve_path(root: Path, raw: Any) -> Path | None:
    if raw in (None, "", "null"):
        return None
    p = Path(str(raw)).expanduser()
    if not p.is_absolute():
        p = (root / p).resolve()
    else:
        p = p.resolve()
    return p


def sibling_root(root: Path, name: str | None = None) -> Path | None:
    """Resolve one sibling directory. name=None → default for this pack."""
    import os

    cfg = siblings_cfg(root)
    pack = os_pack(root)
    if name is None:
        name = _DEFAULT_SIBLING_FOR_PACK.get(pack, "source")
        if name == pack:
            for alt in SIBLING_ORDER:
                if alt != pack and (cfg.get(alt) or {}).get("enabled"):
                    name = alt
                    break
    entry = cfg.get(name) or {}
    env_name = str(entry.get("env") or _DEFAULT_ENV.get(name) or "")
    if env_name:
        env = os.environ.get(env_name)
        if env:
            p = Path(env).expanduser().resolve()
            if p.is_dir():
                return p
    if not entry.get("enabled"):
        return None
    p = _resolve_path(root, entry.get("path"))
    if p is None:
        return None
    return p if p.is_dir() else p


def iter_enabled_siblings(root: Path) -> list[tuple[str, Path]]:
    out: list[tuple[str, Path]] = []
    cfg = siblings_cfg(root)
    pack = os_pack(root)
    for name in SIBLING_ORDER:
        if name == pack:
            continue
        entry = cfg.get(name) or {}
        if not entry.get("enabled") and not entry.get("path"):
            continue
        p = sibling_root(root, name)
        if p is not None and p.is_dir():
            out.append((name, p))
    return out


def include_roots(root: Path) -> list[str]:
    roots = (load_os(root).get("include_roots") or []) or []
    return [str(x) for x in roots]


def legacy_roots(root: Path) -> list[str]:
    roots = (load_os(root).get("legacy_roots") or []) or []
    return [str(x) for x in roots]
