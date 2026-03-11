#!/usr/bin/env python3
"""CLI wrapper for shared skill runtime validation."""

from __future__ import annotations

import sys

from runtime_support import validation_cli


if __name__ == "__main__":
    raise SystemExit(validation_cli(sys.argv[1:]))
