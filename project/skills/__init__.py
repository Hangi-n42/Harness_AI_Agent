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
from skills.workflow_skill import WorkflowSkill

__all__ = [
    "Skill",
    "SkillResult",
    "KnowledgeSkill",
    "CampusSkill",
    "LibrarySkill",
    "TranslationSkill",
    "SummarySkill",
    "WorkflowSkill",
    "FallbackSkill",
    "build_skills",
]


def build_skills() -> list[Skill]:
    # WorkflowSkill first: it only matches compound "summarize + translate"
    # requests, which is more specific than a plain TranslationSkill match.
    return [WorkflowSkill(), TranslationSkill(), LibrarySkill(), CampusSkill(), FallbackSkill()]
