#!/usr/bin/env python3
"""Capture the isolated R030 proof through the shared Simulator runner."""

from __future__ import annotations

import sys

from capture_hybrid_r029_simulator import main


if __name__ == "__main__":
    sys.argv[1:1] = ["--revision", "r030"]
    raise SystemExit(main())
