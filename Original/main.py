"""CampusBot starter: one page, one backend file, one prompt, and one model."""

from __future__ import annotations

import json
import os
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:1.7b")

SYSTEM_PROMPT = (ROOT / "prompt.txt").read_text(encoding="utf-8")
KNOWLEDGE = json.loads((ROOT / "knowledge.json").read_text(encoding="utf-8"))


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)


class ChatResponse(BaseModel):
    response: str


def ask_model(message: str) -> str:
    user_prompt = (
        f"Knowledge context:\n{json.dumps(KNOWLEDGE, ensure_ascii=False, indent=2)}\n\n"
        f"User question:\n{message}"
    )
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.0,
            "num_ctx": 4096,
            "seed": 42,
        },
    }

    try:
        response = httpx.post(OLLAMA_URL, json=payload, timeout=90)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail="The local model is unavailable. Start Ollama and check qwen3:1.7b.",
        ) from exc

    answer = response.json().get("message", {}).get("content", "").strip()
    if not answer:
        raise HTTPException(status_code=502, detail="The model returned an empty response.")
    return answer


app = FastAPI(title="CampusBot Starter", version="0.1.0")
app.mount("/static", StaticFiles(directory=WEB_ROOT), name="static")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(WEB_ROOT / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    return ChatResponse(response=ask_model(request.message))


if __name__ == "__main__":
    host = os.getenv("CAMPUSBOT_HOST", "127.0.0.1")
    port = int(os.getenv("CAMPUSBOT_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
