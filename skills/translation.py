"""translation.py — translate the requested text (no knowledge gate)."""

from __future__ import annotations

from skills.base import Skill, SkillResult


class TranslationSkill(Skill):
    name = "translation"
    description = "Translate the requested text between Chinese and English."
    keywords = (
        "翻译", "translate", "translation", "译成", "翻成", "译成中文", "译成英文",
        "in english", "in chinese", "用中文", "用英文",
    )

    def run(self, text: str, llm) -> SkillResult:
        # Translation is always "answerable" — no knowledge to look up.
        return self._invoke(text, llm)
