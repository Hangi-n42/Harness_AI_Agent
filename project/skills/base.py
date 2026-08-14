"""skills.base — the Skill contract.

Every skill exposes:

* a clear responsibility (``name`` + ``description``),
* its own independent prompt,
* a deterministic ``can_handle`` predicate used by the router,
* a ``run`` method that returns a ``SkillResult`` and never raises for normal
  flow (a down model becomes ``status="error"``).

The "information unavailable" outcome is a first-class result.  Knowledge
skills gate on a deterministic lookup and return ``status="unavailable"``
*before* consulting the model, which structurally prevents hallucination.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from paths import load_knowledge, load_prompt

UNAVAILABLE_TEXT = "That information is not available in the starter knowledge base."


@dataclass
class SkillResult:
    skill: str
    text: str
    ok: bool = True
    status: str = "ok"  # ok | unavailable | error | denied

    def as_dict(self) -> dict:
        return {
            "skill": self.skill,
            "status": self.status,
            "response": self.text,
            "ok": self.ok,
        }


class Skill:
    name: str = ""
    description: str = ""
    keywords: tuple[str, ...] = ()

    def can_handle(self, text: str) -> bool:
        low = text.lower()
        return any(k in low for k in self.keywords)

    def system_prompt(self) -> str:
        return load_prompt(self.name)

    def build_user_prompt(self, text: str, facts: dict | None = None) -> str:
        return text

    def run(self, text: str, llm) -> SkillResult:
        return self._invoke(text, llm)

    def _invoke(self, text: str, llm, facts: dict | None = None) -> SkillResult:
        system = self.system_prompt()
        user = self.build_user_prompt(text, facts)
        try:
            answer = llm.generate(system, user)
        except Exception as exc:  # noqa: BLE001 — a down model must not crash the turn
            return SkillResult(self.name, f"Model error: {exc}", ok=False, status="error")
        if not answer or not answer.strip():
            return SkillResult(self.name, UNAVAILABLE_TEXT, ok=False, status="error")
        return SkillResult(self.name, answer.strip(), ok=True, status="ok")


class KnowledgeSkill(Skill):
    """A skill backed by a fixed JSON knowledge slice.

    ``match_facts(text)`` returns a dict of relevant facts, or ``None`` when the
    question cannot be answered from the slice.  ``run`` turns ``None`` into the
    deterministic "unavailable" outcome without calling the model.
    """

    facts_key: str = ""  # top-level key in knowledge.json

    def knowledge(self) -> dict:
        return load_knowledge().get(self.facts_key, {})

    def match_facts(self, text: str) -> dict | None:
        return self.knowledge() or None

    def build_user_prompt(self, text: str, facts: dict | None = None) -> str:
        facts = facts if facts is not None else self.match_facts(text)
        ctx = json.dumps(facts, ensure_ascii=False, indent=2)
        return f"Knowledge context:\n{ctx}\n\nUser question:\n{text}"

    def run(self, text: str, llm) -> SkillResult:
        facts = self.match_facts(text)
        if facts is None:
            return SkillResult(self.name, UNAVAILABLE_TEXT, ok=False, status="unavailable")
        return self._invoke(text, llm, facts=facts)
