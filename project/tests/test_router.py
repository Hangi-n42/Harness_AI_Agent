"""Routing tests."""

from __future__ import annotations

import unittest


class RouterTests(unittest.TestCase):
    def setUp(self) -> None:
        from runtime.router import SkillRouter
        from skills import build_skills

        self.router = SkillRouter({skill.name: skill for skill in build_skills()})

    def test_campus_question_routes_to_campus_skill(self) -> None:
        skill = self.router.select("What is Shenzhen University's motto?")
        self.assertEqual(skill.name, "campus")

    def test_library_question_routes_to_library_skill(self) -> None:
        skill = self.router.select("Where is the library?")
        self.assertEqual(skill.name, "library")

    def test_translation_request_routes_to_translation_skill(self) -> None:
        skill = self.router.select("Translate 'hello' into Chinese")
        self.assertEqual(skill.name, "translation")

    def test_unrelated_request_is_not_misrouted_to_a_real_skill(self) -> None:
        skill = self.router.select("What is the weather today?")
        self.assertEqual(skill.name, "fallback")


if __name__ == "__main__":
    unittest.main()
