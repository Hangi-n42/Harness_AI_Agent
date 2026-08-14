"""app.py — the FastAPI application and HTTP routes.

Kept separate from main.py so the app can be built against any Runtime (the
real one in production, a fake one in tests).  The ``/chat`` response keeps the
``response`` field the web front-end reads, and adds the structured agent
contract: skill, status, request_id and duration_ms.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from paths import WEB_ROOT  # noqa: E402
from runtime import Runtime  # noqa: E402


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    role: str = Field(default="guest", pattern="^(guest|member|administrator)$")


class WorkflowRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    role: str = Field(default="member", pattern="^(guest|member|administrator)$")
    workflow: str = Field(default="knowledge_summary_translation")


class ChatResponse(BaseModel):
    response: str
    skill: str = ""
    status: str = "ok"
    request_id: str = ""
    duration_ms: float = 0.0
    steps: list[dict] = []


def create_app(runtime: Runtime) -> FastAPI:
    app = FastAPI(title="CampusBot", version="2.0.0")
    app.mount("/static", StaticFiles(directory=WEB_ROOT), name="static")

    @app.get("/", include_in_schema=False)
    def home() -> FileResponse:
        return FileResponse(WEB_ROOT / "index.html")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/chat", response_model=ChatResponse)
    def chat(request: ChatRequest) -> ChatResponse:
        message = request.message.strip()
        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty.")
        out = runtime.handle(message, role=request.role)
        return ChatResponse(
            response=out["response"],
            skill=out["skill"],
            status=out["status"],
            request_id=out["request_id"],
            duration_ms=out["duration_ms"],
            steps=out.get("steps", []),
        )

    @app.post("/workflow", response_model=ChatResponse)
    def workflow(request: WorkflowRequest) -> ChatResponse:
        message = request.message.strip()
        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty.")
        out = runtime.handle_workflow(request.workflow, message, role=request.role)
        return ChatResponse(
            response=out["response"],
            skill=out["skill"],
            status=out["status"],
            request_id=out["request_id"],
            duration_ms=out["duration_ms"],
            steps=out.get("steps", []),
        )

    return app
