"""test_runtime.py — the orchestration layer returns a structured contract."""

from __future__ import annotations

import unittest

from helpers import ExplodingLLM, FakeLLM
from runtime import Runtime


class RuntimeTest(unittest.TestCase):
    def test_handle_returns_structured_contract(self):
        rt = Runtime(llm=FakeLLM(answer="SZU was founded in 1983."))
        out = rt.handle("深圳大学什么时候建校？")
        self.assertTrue({"request_id", "skill", "status", "response", "duration_ms"} <= set(out))
        self.assertEqual(out["skill"], "campus")
        self.assertEqual(out["status"], "ok")

    def test_handle_survives_down_model(self):
        rt = Runtime(llm=ExplodingLLM())
        out = rt.handle("深圳大学的校训是什么？")
        self.assertEqual(out["status"], "error")
        self.assertEqual(out["skill"], "campus")


if __name__ == "__main__":
    unittest.main()
