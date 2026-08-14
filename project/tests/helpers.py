"""helpers.py — test doubles (no third-party deps, no network, no Ollama)."""

from __future__ import annotations


class FakeLLM:
    """Deterministic stand-in for the LLM backend.

    Records every call so tests can assert (a) what the model would have
    received and (b) that a gated skill never consulted the model at all.
    """

    def __init__(self, answer: str = "(mock answer)"):
        self.answer = answer
        self.calls: list[tuple[str, str]] = []

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append((system_prompt, user_prompt))
        return self.answer


class ExplodingLLM(FakeLLM):
    """Raises to simulate a down model — exercises the error path."""

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append((system_prompt, user_prompt))
        raise RuntimeError("connection refused")
