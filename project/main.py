"""CampusBot launch entry point (required by CampusBot Launcher.app, keep thin)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Some bundled/embeddable Python distributions (notably Windows's python._pth
# setup) don't add this script's own directory to sys.path automatically, so
# sibling packages like api/, governance/, runtime/ can't be imported without
# this. Standard installs already have it on sys.path; this is a harmless no-op there.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uvicorn

from api.server import app

if __name__ == "__main__":
    host = os.getenv("CAMPUSBOT_HOST", "127.0.0.1")
    port = int(os.getenv("CAMPUSBOT_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
