"""CampusBot launch entry point (required by CampusBot Launcher.app, keep thin)."""

from __future__ import annotations

import os

import uvicorn

from api.server import app

if __name__ == "__main__":
    host = os.getenv("CAMPUSBOT_HOST", "127.0.0.1")
    port = int(os.getenv("CAMPUSBOT_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
