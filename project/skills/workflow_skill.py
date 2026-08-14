"""workflow_skill.py — Skill Composition (Bonus 3): campus knowledge -> summary -> translation.

Wraps runtime.workflow.Workflow as a single Skill so the composite pipeline
plugs into the same Router/AgentRuntime as every other Skill, with no new
endpoint needed. can_handle() only matches requests that ask for BOTH a
summary and a translation, so plain campus/translation questions still go to
their own dedicated Skill.
"""

from __future__ import annotations

from runtime.workflow import Workflow
from skills.base import Skill, SkillResult
from skills.campus import CampusSkill
from skills.summary import SummarySkill
from skills.translation import TranslationSkill

SUMMARY_WORDS = ("summarize", "summarise", "总结", "概括", "摘要")
TRANSLATE_WORDS = (
    "translate", "translation", "译成", "翻成",
    "in chinese", "in english", "用中文", "用英文",
)


class WorkflowSkill(Skill):
    name = "workflow"
    description = "Composite Skill: look up campus facts, summarise them, then translate the summary."

    def can_handle(self, text: str) -> bool:
        low = text.lower()
        return any(w in low for w in SUMMARY_WORDS) and any(w in low for w in TRANSLATE_WORDS)

    def run(self, text: str, llm) -> SkillResult:
        target = "Chinese" if any(w in text.lower() for w in ("chinese", "中文")) else "English"
        pipeline = Workflow(
            "knowledge_summary_translation",
            [
                lambda t: CampusSkill().run(t, llm),
                lambda t: SummarySkill().run(t, llm),
                lambda t: TranslationSkill().run(
                    f"Translate the following text into {target}:\n{t}", llm
                ),
            ],
        )
        final = pipeline.run(text)[-1]
        return SkillResult(self.name, final.text, ok=final.ok, status=final.status)
