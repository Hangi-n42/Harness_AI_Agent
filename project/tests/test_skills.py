"""test_skills.py — skill behaviour, including the no-hallucination gate."""

from __future__ import annotations

import unittest

from helpers import FakeLLM
from skills.campus import CampusSkill
from skills.fallback import FallbackSkill
from skills.library import LibrarySkill
from skills.translation import TranslationSkill


class CampusSkillTest(unittest.TestCase):
    def test_motto_matches(self):
        facts = CampusSkill().match_facts("深圳大学的校训是什么？")
        self.assertIn("motto", facts)
        self.assertTrue(facts["motto"].startswith("self-reliance"))


class LibrarySkillTest(unittest.TestCase):
    def test_address_matches(self):
        facts = LibrarySkill().match_facts("图书馆的地址是哪里？")
        self.assertIn("official_address", facts)
        self.assertIn("3688", facts["official_address"])

    def test_unavailable_no_hallucination(self):
        # Opening hours are NOT in the knowledge base.  The skill must refuse
        # *without ever calling the model* — the deterministic gate fires first.
        llm = FakeLLM(answer="The library opens at 8am")  # would hallucinate if called
        res = LibrarySkill().run("图书馆的开放时间是几点？", llm)
        self.assertEqual(res.status, "unavailable")
        self.assertFalse(res.ok)
        self.assertEqual(llm.calls, [])


class TranslationSkillTest(unittest.TestCase):
    def test_always_available(self):
        llm = FakeLLM(answer="Hello")
        res = TranslationSkill().run("翻译：你好", llm)
        self.assertEqual(res.status, "ok")
        self.assertEqual(res.text, "Hello")


class FallbackSkillTest(unittest.TestCase):
    def test_deterministic_and_offline(self):
        llm = FakeLLM(answer="SHOULD NOT BE USED")
        res = FallbackSkill().run("今天天气怎么样？", llm)
        self.assertEqual(res.status, "unavailable")
        self.assertEqual(llm.calls, [])


if __name__ == "__main__":
    unittest.main()
