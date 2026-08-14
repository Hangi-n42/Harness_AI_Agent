"""AgentRuntime — orchestrates guardrail -> router -> skill -> audit log.

Ported from the teammate's original design; the only functional change is
calling ``skill.run(message, llm)`` (the skills/ package's real contract)
instead of the ``skill.execute(message)`` it was originally written against.
"""

from __future__ import annotations

import time
import uuid


class AgentRuntime:
    def __init__(self, router, llm, guardrail=None, logger=None):
        self.router = router
        self.llm = llm
        self.guardrail = guardrail
        self.logger = logger

    def run(self, message, user="guest"):
        start = time.time()
        request_id = str(uuid.uuid4())[:8]

        if not isinstance(message, str) or not message.strip():
            return self._finish(request_id, None, "error", "请输入有效的问题。", start, user)

        message = message.strip()

        if self.guardrail is not None:
            allowed, reason = self.guardrail.check(message)
            if not allowed:
                return self._finish(request_id, None, "blocked", reason, start, user)

        skill = self.router.select(message)
        if skill is None:
            return self._finish(request_id, None, "unmatched", "暂时无法匹配合适的功能。", start, user)

        try:
            result = skill.run(message, self.llm)
            status = "unmatched" if skill.name == "fallback" else result.status
            if status == "ok":
                status = "success"
            return self._finish(request_id, skill.name, status, result.text, start, user)
        except Exception as exc:  # noqa: BLE001 — a broken skill must not crash the turn
            print("Runtime error:", exc)
            return self._finish(
                request_id, getattr(skill, "name", None), "failed",
                "该功能执行失败，请稍后重试。", start, user,
            )

    def _finish(self, request_id, skill_name, status, response, start, user) -> dict:
        result = {
            "request_id": request_id,
            "skill": skill_name,
            "status": status,
            "response": response,
            "duration": round(time.time() - start, 3),
        }
        if self.logger is not None:
            self.logger.write(user=user, skill=skill_name, status=status, duration=result["duration"])
        return result
