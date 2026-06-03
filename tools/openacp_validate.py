#!/usr/bin/env python3
"""Compatibility wrapper for running the OpenACP validator from a source tree."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from openacp.validate import main


if __name__ == "__main__":
    raise SystemExit(main())
