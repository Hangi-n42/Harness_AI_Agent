"""Skill Composition tests (Bonus 3): knowledge -> summary -> translation."""

from __future__ import annotations

import unittest


class FakeLLM:
    def __init__(self, answer: str = "FAKE ANSWER") -> None:
        self.answer = answer
        self.calls = 0

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        return self.answer


class WorkflowSkillTests(unittest.TestCase):
    def setUp(self) -> None:
        from skills.workflow_skill import WorkflowSkill

        self.skill = WorkflowSkill()

    def test_can_handle_requires_both_summary_and_translation_intent(self) -> None:
        self.assertTrue(self.skill.can_handle("Summarize the motto and translate it into Chinese"))
        self.assertFalse(self.skill.can_handle("What is the motto?"))
        self.assertFalse(self.skill.can_handle("Translate 'hello' into Chinese"))

    def test_runs_knowledge_then_summary_then_translation_in_order(self) -> None:
        llm = FakeLLM(answer="ok")
        result = self.skill.run("Summarize the motto and translate it into Chinese", llm)
        self.assertEqual(result.status, "ok")
        # 3 model calls: CampusSkill phrases the fact, then summary, then translation.
        # Only a knowledge *miss* skips the model entirely (see the short-circuit test below).
        self.assertEqual(llm.calls, 3)

    def test_missing_knowledge_short_circuits_before_any_model_call(self) -> None:
        llm = FakeLLM()
        result = self.skill.run(
            "Summarize the international office location and translate it into Chinese", llm
        )
        self.assertEqual(result.status, "unavailable")
        self.assertEqual(llm.calls, 0)


if __name__ == "__main__":
    unittest.main()
