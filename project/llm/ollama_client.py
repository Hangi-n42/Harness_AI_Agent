"""Ollama call wrapper."""

from __future__ import annotations

import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:1.7b")


def ask_model(system_prompt: str, user_prompt: str) -> str:
    import httpx  # imported lazily so tests don't need it installed to exercise routing/skills

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
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
    response = httpx.post(OLLAMA_URL, json=payload, timeout=90)
    response.raise_for_status()
    return response.json().get("message", {}).get("content", "").strip()


class OllamaLLM:
    """Adapter exposing the generate(system, user) -> str contract skills expect."""

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        return ask_model(system_prompt, user_prompt)
