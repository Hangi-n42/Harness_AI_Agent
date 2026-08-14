"""test_api.py — the HTTP layer wires runtime output into the agent contract.

Uses FastAPI's ``TestClient`` (httpx) with a ``FakeLLM`` backend, so the whole
request path — routing, composition, RBAC, structured response — is exercised
against the real dependency versions shipped in the course bundle, still with
no Ollama and no network.
"""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app import create_app
from helpers import FakeLLM
from runtime import Runtime
from workflow import KNOWLEDGE_SUMMARY_TRANSLATION


class ApiContractTest(unittest.TestCase):
    def setUp(self):
        self.rt = Runtime(llm=FakeLLM(answer="(ok)"))
        self.client = TestClient(create_app(runtime=self.rt))

    def test_health(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"status": "ok"})

    def test_chat_returns_structured_contract(self):
        r = self.client.post("/chat", json={"message": "深圳大学的校训是什么？"})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["skill"], "campus")
        self.assertEqual(data["status"], "ok")
        self.assertIn("request_id", data)
        self.assertIn("duration_ms", data)
        self.assertIn("steps", data)

    def test_chat_auto_composes_multi_skill_request(self):
        r = self.client.post("/chat", json={
            "message": "总结深圳大学的校训并翻译成中文",
            "role": "member",
        })
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["skill"], KNOWLEDGE_SUMMARY_TRANSLATION)
        self.assertEqual(
            [s["skill"] for s in data["steps"]],
            ["campus", "summary", "translation"],
        )

    def test_workflow_endpoint_runs_composition(self):
        r = self.client.post("/workflow", json={
            "message": "总结深圳大学的校训并翻译成中文",
            "role": "member",
        })
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["skill"], KNOWLEDGE_SUMMARY_TRANSLATION)
        self.assertEqual(data["status"], "ok")

    def test_workflow_endpoint_unknown_workflow(self):
        r = self.client.post("/workflow", json={
            "message": "anything",
            "role": "member",
            "workflow": "does_not_exist",
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "error")


if __name__ == "__main__":
    unittest.main()
