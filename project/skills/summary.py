"""summary.py — summarise a supplied passage into a concise version.

Unlike the knowledge skills, ``SummarySkill`` is a *transform* skill: it always
runs (there is nothing to look up), and it condenses whatever text it is given
into a short, plain-text summary.  It is used both on its own and as the middle
stage of the knowledge -> summary -> translation workflow.
"""

from __future__ import annotations

from skills.base import Skill, SkillResult


class SummarySkill(Skill):
    name = "summary"
    description = "Summarise the supplied passage into a short, plain-text summary."
    keywords = (
        "总结", "概括", "摘要", "归纳", "简写", "summarize", "summarise", "summary",
    )

    def build_user_prompt(self, text: str, facts: dict | None = None) -> str:
        return f"Text to summarise:\n{text}"

    def run(self, text: str, llm) -> SkillResult:
        # Summarising is always "answerable" — no knowledge to look up.
        return self._invoke(text, llm)
