"""fallback.py — handle requests outside the known skill domains.

Always matches, so the router only reaches it after every real skill declined.
The answer is deterministic and never consults the model.
"""

from __future__ import annotations

from skills.base import Skill, SkillResult

FALLBACK_TEXT = (
    "Sorry, I can only help with Shenzhen University facts, the library, or "
    "translation. Please try one of those topics."
)


class FallbackSkill(Skill):
    name = "fallback"
    description = "Handle requests outside the known skill domains."
    keywords = ()  # never keyword-matched; it is the router's last resort

    def can_handle(self, text: str) -> bool:
        return True

    def run(self, text: str, llm) -> SkillResult:
        return SkillResult(self.name, FALLBACK_TEXT, ok=False, status="unavailable")
