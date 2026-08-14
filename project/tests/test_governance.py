"""test_governance.py — audit log and permission policy."""

from __future__ import annotations

import unittest

from governance import AuditLog, PermissionPolicy
from helpers import FakeLLM
from runtime import Runtime


class AuditLogTest(unittest.TestCase):
    def test_records_metadata_only(self):
        log = AuditLog()  # no path -> in-memory buffer
        rt = Runtime(llm=FakeLLM(), governance=log)
        rt.handle("深圳大学的校训是什么？", role="guest")

        entries = log.entries()
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        # Required metadata present...
        self.assertTrue({"request_id", "role", "skill", "status", "duration_ms"} <= set(entry))
        self.assertEqual(entry["skill"], "campus")
        self.assertEqual(entry["status"], "ok")
        # ...and no sensitive content (user message text) is ever stored.
        self.assertNotIn("text", entry)
        self.assertNotIn("message", entry)


class PermissionPolicyTest(unittest.TestCase):
    def test_denied_for_restricted_role(self):
        policy = PermissionPolicy(
            rules={
                "guest": {"campus", "library", "fallback"},  # translation revoked
                "administrator": {"campus", "library", "translation", "fallback"},
            }
        )
        rt = Runtime(llm=FakeLLM(answer="Hello"), policy=policy)

        denied = rt.handle("翻译：你好", role="guest")
        self.assertEqual(denied["status"], "denied")

        allowed = rt.handle("翻译：你好", role="administrator")
        self.assertEqual(allowed["status"], "ok")
        self.assertEqual(allowed["skill"], "translation")

    def test_default_policy_allows_public_skills(self):
        policy = PermissionPolicy()
        self.assertTrue(policy.authorize("guest", "campus"))
        self.assertTrue(policy.authorize("member", "library"))
        self.assertTrue(policy.authorize("administrator", "translation"))


if __name__ == "__main__":
    unittest.main()
