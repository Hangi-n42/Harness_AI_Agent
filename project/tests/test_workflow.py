"""test_workflow.py — Bonus 3: multi-skill composition (knowledge -> summary -> translation)."""

from __future__ import annotations

import unittest

from governance import AuditLog, PermissionPolicy
from helpers import FakeLLM
from runtime import Runtime
from skills.base import UNAVAILABLE_TEXT
from workflow import build_knowledge_summary_translation, KNOWLEDGE_SUMMARY_TRANSLATION


class EchoLLM:
    """Returns its input, tagged, so tests can prove output truly threads
    stage -> stage (rather than a fixed canned answer)."""

    def __init__(self, tag: str):
        self.tag = tag
        self.calls: list[tuple[str, str]] = []

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append((system_prompt, user_prompt))
        return f"{self.tag}:{user_prompt}"


class WorkflowTest(unittest.TestCase):
    def test_composes_three_stages_and_threads_output(self):
        llm = EchoLLM("E")
        wf = build_knowledge_summary_translation(llm)
        results = wf.run("总结深圳大学的校训并翻译成中文")

        self.assertEqual([r.skill for r in results], ["campus", "summary", "translation"])
        self.assertTrue(all(r.ok for r in results))

        # Stage 1 is deterministic (facts JSON), stages 2 and 3 hit the model.
        self.assertEqual(len(llm.calls), 2)

        # Stage 2 (summary) received the stage-1 facts; stage 3 (translation)
        # received the stage-2 summary — output is threaded, not dropped.
        summary_user = llm.calls[0][1]
        translation_user = llm.calls[1][1]
        self.assertIn("self-reliance", summary_user)          # facts flowed in
        self.assertIn(summary_user, translation_user)          # summary flowed in
        self.assertIn("Chinese", translation_user)             # target language set
        self.assertEqual(results[-1].text, f"E:{translation_user}")


class WorkflowShortCircuitTest(unittest.TestCase):
    def test_missing_knowledge_stops_before_any_model_call(self):
        # "开放时间" is not in the campus knowledge slice -> stage 1 returns
        # unavailable, so summary/translation must never touch the model.
        llm = FakeLLM(answer="would hallucinate")
        wf = build_knowledge_summary_translation(llm)
        results = wf.run("总结图书馆开放时间并翻译成英文")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].skill, "campus")
        self.assertEqual(results[0].status, "unavailable")
        self.assertEqual(results[0].text, UNAVAILABLE_TEXT)
        self.assertEqual(llm.calls, [])


class RuntimeWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.rt = Runtime(llm=FakeLLM(answer="ok"))

    def test_routes_compose_request_to_workflow(self):
        out = self.rt.handle("总结深圳大学的校训并翻译成中文", role="member")
        self.assertEqual(out["skill"], KNOWLEDGE_SUMMARY_TRANSLATION)
        self.assertEqual(out["status"], "ok")
        self.assertEqual([s["skill"] for s in out["steps"]],
                         ["campus", "summary", "translation"])

    def test_plain_translation_does_not_compose(self):
        # Asking only to translate must NOT trigger the workflow.
        out = self.rt.handle("翻译：你好", role="member")
        self.assertEqual(out["skill"], "translation")
        self.assertEqual(out["steps"], [])

    def test_workflow_denied_when_one_stage_revoked(self):
        policy = PermissionPolicy(
            rules={
                "guest": {"campus", "library", "fallback"},  # summary+translation revoked
                "administrator": {"campus", "library", "translation", "summary", "fallback"},
            }
        )
        rt = Runtime(llm=FakeLLM(answer="ok"), policy=policy)

        denied = rt.handle("总结深圳大学的校训并翻译成中文", role="guest")
        self.assertEqual(denied["status"], "denied")

        allowed = rt.handle("总结深圳大学的校训并翻译成中文", role="administrator")
        self.assertEqual(allowed["status"], "ok")

    def test_workflow_creates_audit_record(self):
        log = AuditLog()
        rt = Runtime(llm=FakeLLM(answer="ok"), governance=log)
        rt.handle("总结深圳大学的校训并翻译成中文", role="member")

        entry = log.entries()[0]
        self.assertEqual(entry["skill"], KNOWLEDGE_SUMMARY_TRANSLATION)
        self.assertEqual(entry["status"], "ok")
        self.assertEqual([s["skill"] for s in entry["steps"]],
                         ["campus", "summary", "translation"])
        # Metadata only — no user text stored.
        self.assertNotIn("text", entry)
        self.assertNotIn("message", entry)

    def test_explicit_unknown_workflow_errors(self):
        out = self.rt.handle_workflow("nope", "anything", role="member")
        self.assertEqual(out["status"], "error")


if __name__ == "__main__":
    unittest.main()
