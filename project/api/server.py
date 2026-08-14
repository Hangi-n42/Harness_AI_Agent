"""FastAPI app, /chat endpoint."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from governance.guardrail import Guardrail
from governance.logger import AuditLogger
from llm.ollama_client import OllamaLLM
from runtime.agent_runtime import AgentRuntime
from runtime.router import SkillRouter
from skills import build_skills

ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web"

app = FastAPI(title="CampusBot Agent Harness", version="0.2.0")
app.mount("/static", StaticFiles(directory=WEB_ROOT), name="static")

_skills = {skill.name: skill for skill in build_skills()}
_runtime = AgentRuntime(
    router=SkillRouter(_skills),
    llm=OllamaLLM(),
    guardrail=Guardrail(),
    logger=AuditLogger(),
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    user: str = "guest"


class ChatResponse(BaseModel):
    request_id: str
    skill: str | None
    status: str
    response: str
    duration: float


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(WEB_ROOT / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    result = _runtime.run(request.message, user=request.user)
    if result["status"] == "blocked":
        raise HTTPException(status_code=400, detail=result["response"])
    return ChatResponse(**result)
