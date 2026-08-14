"""workflow.py — Bonus 3: compose multiple skills into one pipeline.

A single user request can now flow through several skills in order, with the
output of each skill becoming the input of the next.  The reference composition
described in the assignment is:

    Knowledge Skill  ->  Summary Skill  ->  Translation Skill
    (deterministic)      (LLM)              (LLM)

Design notes
------------
* ``Workflow`` is generic: it is just an ordered list of *stage* callables.
  Each stage is ``(text) -> SkillResult``, so any skill (or custom stage) can
  be plugged in without changing the pipeline itself.
* The pipeline stops at the first non-``ok`` stage.  Because the knowledge
  stage reuses ``CampusSkill.match_facts`` — the deterministic gate that
  returns ``None`` (-> ``unavailable``) before the model is consulted — a
  missing fact can never be summarised or translated.  Hallucination is
  structurally impossible across the whole workflow.
* Stages reuse the public ``Skill.run`` / ``Skill.match_facts`` API, so error
  handling (a down model becomes ``status="error"``) is inherited for free.
"""

from __future__ import annotations

import json

from skills.base import SkillResult, UNAVAILABLE_TEXT
from skills.campus import CampusSkill
from skills.summary import SummarySkill
from skills.translation import TranslationSkill

# The one composed workflow the assignment asks for.  Keep the name stable —
# the runtime and the API reference it by this key.
KNOWLEDGE_SUMMARY_TRANSLATION = "knowledge_summary_translation"


class Workflow:
    """An ordered pipeline of stages.  ``run`` threads output -> input."""

    def __init__(self, name: str, stages: list, skills: tuple[str, ...] = ()):
        self.name = name
        self.stages = stages
        # Names of the skills this workflow depends on, used by the runtime
        # for RBAC: a role may run the workflow only if it may use every skill.
        self.skills = skills

    def run(self, text: str) -> list[SkillResult]:
        results: list[SkillResult] = []
        current = text
        for stage in self.stages:
            result = stage(current)
            results.append(result)
            if not result.ok:
                break  # short-circuit: don't build on a failed stage
            current = result.text
        return results


def build_knowledge_summary_translation(
    llm,
    knowledge: CampusSkill | None = None,
    summary: SummarySkill | None = None,
    translation: TranslationSkill | None = None,
    target_language: str = "Chinese",
) -> Workflow:
    """Build the reference composition: knowledge -> summary -> translation.

    Stage 1 is deterministic (no model call): it pulls the relevant facts from
    the campus knowledge slice.  Stage 2 asks the model to summarise those
    facts.  Stage 3 asks the model to translate the summary into
    ``target_language``.
    """
    knowledge = knowledge or CampusSkill()
    summary = summary or SummarySkill()
    translation = translation or TranslationSkill()

    def knowledge_stage(text: str) -> SkillResult:
        facts = knowledge.match_facts(text)
        if facts is None:
            return SkillResult(
                knowledge.name, UNAVAILABLE_TEXT, ok=False, status="unavailable"
            )
        return SkillResult(
            knowledge.name,
            json.dumps(facts, ensure_ascii=False, indent=2),
            ok=True,
            status="ok",
        )

    def summary_stage(text: str) -> SkillResult:
        return summary.run(text, llm)

    def translation_stage(text: str) -> SkillResult:
        # Give the translation skill an explicit target so the stage behaves the
        # same regardless of how the original question was phrased.
        instruction = f"Translate the following text into {target_language}:\n{text}"
        return translation.run(instruction, llm)

    return Workflow(
        name=KNOWLEDGE_SUMMARY_TRANSLATION,
        stages=[knowledge_stage, summary_stage, translation_stage],
        skills=(knowledge.name, summary.name, translation.name),
    )


def build_workflows(llm) -> dict[str, Workflow]:
    """Return the map of available composed workflows keyed by name."""
    return {
        KNOWLEDGE_SUMMARY_TRANSLATION: build_knowledge_summary_translation(llm),
    }
