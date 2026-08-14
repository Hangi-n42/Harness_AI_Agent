"""SkillRouter — selects a Skill by delegating to each skill's own can_handle().

Keyword matching lives once, on each Skill (see skills/*.py); the router does
not duplicate it, so a skill's routing rules stay in one place.
"""

from __future__ import annotations


class SkillRouter:
    def __init__(self, skills: dict):
        self.skills = skills  # name -> Skill instance, in routing-priority order

    def select(self, message: str):
        for skill in self.skills.values():
            if skill.can_handle(message):
                return skill
        return None
