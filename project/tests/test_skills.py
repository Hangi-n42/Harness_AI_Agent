"""Skill tests."""

from __future__ import annotations

import unittest


class FakeLLM:
    def __init__(self, answer: str = "FAKE ANSWER") -> None:
        self.answer = answer
        self.calls = 0

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        return self.answer


class CampusSkillTests(unittest.TestCase):
    def setUp(self) -> None:
        from skills.campus import CampusSkill

        self.skill = CampusSkill()

    def test_returns_motto_for_known_question(self) -> None:
        llm = FakeLLM()
        result = self.skill.run("What is the university's motto?", llm)
        self.assertEqual(result.status, "ok")
        self.assertEqual(llm.calls, 1)

    def test_missing_knowledge_does_not_invent_an_answer(self) -> None:
        llm = FakeLLM()
        result = self.skill.run("Who is the current president?", llm)
        self.assertEqual(result.status, "unavailable")
        self.assertFalse(result.ok)
        self.assertEqual(llm.calls, 0)  # model must not be consulted


class LibrarySkillTests(unittest.TestCase):
    def setUp(self) -> None:
        from skills.library import LibrarySkill

        self.skill = LibrarySkill()

    def test_returns_library_location(self) -> None:
        llm = FakeLLM()
        result = self.skill.run("Where is the library?", llm)
        self.assertEqual(result.status, "ok")

    def test_unrelated_library_question_is_unavailable(self) -> None:
        llm = FakeLLM()
        result = self.skill.run("What time does the library open?", llm)
        self.assertEqual(result.status, "unavailable")
        self.assertEqual(llm.calls, 0)


class TranslationSkillTests(unittest.TestCase):
    def test_translates_requested_text_only(self) -> None:
        from skills.translation import TranslationSkill

        llm = FakeLLM(answer="你好")
        result = TranslationSkill().run("Translate 'hello' into Chinese", llm)
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.text, "你好")


class FallbackSkillTests(unittest.TestCase):
    def test_always_matches_and_never_calls_the_model(self) -> None:
        from skills.fallback import FallbackSkill

        skill = FallbackSkill()
        llm = FakeLLM()
        self.assertTrue(skill.can_handle("anything at all"))
        result = skill.run("anything at all", llm)
        self.assertEqual(result.status, "unavailable")
        self.assertEqual(llm.calls, 0)


if __name__ == "__main__":
    unittest.main()
