"""runtime/workflow.py — a generic Skill pipeline (Bonus 3: Skill Composition).

Each stage's output text feeds the next stage's input. Any stage returning
``ok=False`` (e.g. a knowledge miss) short-circuits the pipeline, so a
downstream stage never asks the model to summarise or translate something
that was never actually found.
"""

from __future__ import annotations

from typing import Callable

from skills.base import SkillResult

Stage = Callable[[str], SkillResult]


class Workflow:
    def __init__(self, name: str, stages: list[Stage]):
        self.name = name
        self.stages = stages

    def run(self, text: str) -> list[SkillResult]:
        results: list[SkillResult] = []
        current = text
        for stage in self.stages:
            result = stage(current)
            results.append(result)
            if not result.ok:
                break
            current = result.text
        return results
