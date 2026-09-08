#!/usr/bin/env python3
"""Compatibility wrapper. Prefer tools/bridge.py."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bridge  # noqa: E402


if __name__ == "__main__":
    # Old: code_bridge.py resolve QUERY  →  bridge resolve QUERY
    # Old: code_bridge.py run -- argv
    argv = sys.argv[1:]
    if argv[:1] == ["run"] and "--repo" not in argv:
        rest = argv[1:]
        sys.argv = [sys.argv[0], "run", *rest]
    raise SystemExit(bridge.main())
