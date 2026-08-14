"""llm.py — a tiny, swappable LLM interface.

The rest of the code depends only on ``backend.generate(system, user) -> str``,
never on a concrete vendor.  This keeps every Skill and the Runtime testable
offline (tests inject a fake backend) and lets us swap the real model with a
one-line change.
"""

from __future__ import annotations

import os

import httpx


class LLMError(RuntimeError):
    """Raised when the local model cannot produce an answer."""


class OllamaBackend:
    """Talks to the bundled local Ollama server."""

    def __init__(self, url: str | None = None, model: str | None = None):
        self.url = url or os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3:0.6b")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "think": False,
            "options": {"temperature": 0.0, "num_ctx": 4096, "seed": 42},
        }
        try:
            response = httpx.post(self.url, json=payload, timeout=90)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMError(
                "The local model is unavailable. Start Ollama and check the model."
            ) from exc

        answer = response.json().get("message", {}).get("content", "").strip()
        if not answer:
            raise LLMError("The model returned an empty response.")
        return answer
