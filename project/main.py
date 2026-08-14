"""main.py — CampusBot entry point (bootstrap).

The macOS launcher always runs this file.  We keep it a thin bootstrap: anchor
the project root on ``sys.path``, wire the real Runtime (Ollama + audit log)
into the FastAPI app, and serve.  ``app`` is also exposed at module level so
the launcher can import it either way.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import uvicorn  # noqa: E402

from app import create_app  # noqa: E402
from governance import AuditLog  # noqa: E402
from llm import OllamaBackend  # noqa: E402
from paths import AUDIT_PATH  # noqa: E402
from runtime import Runtime  # noqa: E402


def build_app():
    runtime = Runtime(
        llm=OllamaBackend(),
        governance=AuditLog(path=AUDIT_PATH),
    )
    return create_app(runtime=runtime)


app = build_app()


if __name__ == "__main__":
    host = os.getenv("CAMPUSBOT_HOST", "127.0.0.1")
    port = int(os.getenv("CAMPUSBOT_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
