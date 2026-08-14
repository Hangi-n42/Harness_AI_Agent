"""summary.py — condense the given text into 1-3 sentences (no knowledge gate)."""

from __future__ import annotations

from skills.base import Skill, SkillResult


class SummarySkill(Skill):
    name = "summary"
    description = "Summarise the given text into 1-3 sentences, preserving exact facts."
    keywords = ("summarize", "summarise", "总结", "概括", "摘要")

    def build_user_prompt(self, text: str, facts: dict | None = None) -> str:
        return f"Text to summarise:\n{text}"

    def run(self, text: str, llm) -> SkillResult:
        return self._invoke(text, llm)
