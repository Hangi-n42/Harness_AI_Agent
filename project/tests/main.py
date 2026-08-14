"""main.py — automated test entry point (macOS bundled runtime).

The macOS procedure runs this file with the package's own Python runtime:

    CAMPUSBOT_PROJECT_ROOT="$PWD/project/tests" \
    CAMPUSBOT_SOURCE_ROOT="$PWD/project" \
    "$APP/Contents/Resources/runtime/server/CampusBotRunner/CampusBotRunner"

``CAMPUSBOT_SOURCE_ROOT`` points at the source root; we discover and run every
``test_*.py`` under ``tests/``.  A successful run ends with ``OK`` and exit 0.
The ``__file__`` fallback also lets us run it with a plain interpreter:

    python3 tests/main.py
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

root = Path(os.environ.get("CAMPUSBOT_SOURCE_ROOT") or Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(root))

suite = unittest.defaultTestLoader.discover(str(root / "tests"), "test_*.py")
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
