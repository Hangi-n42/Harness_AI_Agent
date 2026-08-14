"""runtime.py — the orchestration layer.

Responsibilities (and *only* these):
  1. receive a user request,
  2. route it to a Skill (deterministic, rule-based, ordered),
  3. enforce the permission policy,
  4. execute the Skill against the LLM,
  5. audit the outcome,
  6. return a structured result.

The Runtime knows nothing about individual skills' prompts or knowledge; it
depends only on the Skill contract defined in ``skills.base``.
"""

from __future__ import annotations

import time
import uuid

from governance import AuditLog, PermissionPolicy
from skills import build_skills
from skills.base import SkillResult
from workflow import build_workflows, KNOWLEDGE_SUMMARY_TRANSLATION


class Runtime:
    # A request is treated as a composed workflow when it explicitly asks for a
    # workflow, or when it asks to *both* summarise and translate in one turn.
    COMPOSE_EXPLICIT = ("工作流", "workflow", "pipeline", "compose", "多技能")
    COMPOSE_SUMMARY = ("总结", "概括", "摘要", "归纳", "summariz", "summaris", "summary")
    COMPOSE_TRANSLATE = ("翻译", "translate", "translation", "译成")

    def __init__(
        self,
        skills=None,
        llm=None,
        governance: AuditLog | None = None,
        policy: PermissionPolicy | None = None,
        workflows: dict | None = None,
    ):
        self.skills = skills if skills is not None else build_skills()
        self.llm = llm
        self.governance = governance
        self.policy = policy or PermissionPolicy()
        self.workflows = workflows if workflows is not None else build_workflows(self.llm)
        # The last skill in the list is the fallback (matches everything).
        self.fallback = self.skills[-1]

    def route(self, text: str):
        """Return the first skill whose ``can_handle`` matches, else fallback."""
        for skill in self.skills:
            if skill.can_handle(text):
                return skill
        return self.fallback

    def route_workflow(self, text: str):
        """Return a composed Workflow when the request asks to combine skills.

        Composition wins over single-skill routing when it applies, so a request
        like "总结深大校训并翻译成中文" runs the whole pipeline instead of being
        claimed by a single skill.
        """
        low = text.lower()
        if any(k in low for k in self.COMPOSE_EXPLICIT):
            return self.workflows.get(KNOWLEDGE_SUMMARY_TRANSLATION)
        wants_summary = any(k in low for k in self.COMPOSE_SUMMARY)
        wants_translate = any(k in low for k in self.COMPOSE_TRANSLATE)
        if wants_summary and wants_translate:
            return self.workflows.get(KNOWLEDGE_SUMMARY_TRANSLATION)
        return None

    def _authorize(self, role: str, skill_names: tuple[str, ...]) -> bool:
        return all(self.policy.authorize(role, name) for name in skill_names)

    def handle(self, text: str, role: str = "guest") -> dict:
        request_id = uuid.uuid4().hex[:12]
        start = time.perf_counter()

        # 1. Composition first: a multi-skill request is one workflow, not a
        #    single skill pick.
        workflow = self.route_workflow(text)
        if workflow is not None:
            return self._run_workflow(workflow, text, role, request_id, start)

        # 2. Otherwise: single-skill routing.
        skill = self.route(text)
        if not self.policy.authorize(role, skill.name):
            result = SkillResult(
                skill.name,
                "You do not have permission to use this capability.",
                ok=False,
                status="denied",
            )
        else:
            result = skill.run(text, self.llm)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        if self.governance is not None:
            # Metadata only — never the user's message text.
            self.governance.audit(
                request_id=request_id,
                role=role,
                skill=skill.name,
                status=result.status,
                duration_ms=duration_ms,
            )

        return {
            "request_id": request_id,
            "skill": skill.name,
            "status": result.status,
            "response": result.text,
            "duration_ms": duration_ms,
            "steps": [],
        }

    def handle_workflow(self, name: str, text: str, role: str = "member") -> dict:
        """Explicitly run a named workflow (used by the ``/workflow`` API)."""
        request_id = uuid.uuid4().hex[:12]
        start = time.perf_counter()
        workflow = self.workflows.get(name)
        if workflow is None:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            return {
                "request_id": request_id,
                "skill": name,
                "status": "error",
                "response": f"Unknown workflow: {name}",
                "duration_ms": duration_ms,
                "steps": [],
            }
        return self._run_workflow(workflow, text, role, request_id, start)

    def _run_workflow(self, workflow, text: str, role: str, request_id: str, start: float) -> dict:
        # RBAC: every skill in the pipeline must be allowed for this role.
        if not self._authorize(role, workflow.skills):
            result = SkillResult(
                workflow.name,
                "You do not have permission to use this capability.",
                ok=False,
                status="denied",
            )
            steps: list[dict] = []
        else:
            results = workflow.run(text)
            steps = [{"skill": r.skill, "status": r.status} for r in results]
            final = results[-1]
            result = SkillResult(workflow.name, final.text, ok=final.ok, status=final.status)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        if self.governance is not None:
            # Metadata only — stage names/statuses, never the user's message text.
            self.governance.audit(
                request_id=request_id,
                role=role,
                skill=workflow.name,
                status=result.status,
                duration_ms=duration_ms,
                steps=steps,
            )

        return {
            "request_id": request_id,
            "skill": workflow.name,
            "status": result.status,
            "response": result.text,
            "duration_ms": duration_ms,
            "steps": steps,
        }
