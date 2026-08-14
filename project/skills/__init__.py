"""skills — the skill registry.

``build_skills`` returns skills in *routing-priority order*: most specific
first, fallback last.  The Runtime iterates this list and returns the first
``can_handle`` match.
"""

from __future__ import annotations

from skills.base import KnowledgeSkill, Skill, SkillResult
from skills.campus import CampusSkill
from skills.fallback import FallbackSkill
from skills.library import LibrarySkill
from skills.summary import SummarySkill
from skills.translation import TranslationSkill

__all__ = [
    "Skill",
    "SkillResult",
    "KnowledgeSkill",
    "CampusSkill",
    "LibrarySkill",
    "SummarySkill",
    "TranslationSkill",
    "FallbackSkill",
    "build_skills",
]


def build_skills() -> list[Skill]:
    return [TranslationSkill(), LibrarySkill(), CampusSkill(), FallbackSkill()]
