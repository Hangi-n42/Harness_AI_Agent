"""paths.py — central path resolution.

The CampusBot launcher runs this code from a bundled, frozen environment where
the current working directory is NOT the project folder.  Every file access is
therefore anchored to the *real* location of this module (``__file__``), never
to ``os.getcwd()`` and never to environment variables:

* In normal launches the runner executes ``project/main.py``.
* In the test procedure the runner executes ``project/tests/main.py`` with
  ``CAMPUSBOT_PROJECT_ROOT`` pointing at ``tests/`` — so relying on that
  variable here would break knowledge/prompt loading.

``Path(__file__).resolve().parent`` is always ``project/`` because this file
physically lives there.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PROMPTS_DIR = ROOT / "prompts"
KNOWLEDGE_PATH = ROOT / "knowledge.json"
WEB_ROOT = ROOT / "web"
AUDIT_PATH = ROOT / "audit.jsonl"


def load_knowledge() -> dict:
    """Load the full knowledge base (skills slice their own section)."""
    return json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8"))


def load_prompt(name: str) -> str:
    """Load a per-skill prompt file, e.g. ``load_prompt("campus")``."""
    return (PROMPTS_DIR / f"{name}.txt").read_text(encoding="utf-8")
