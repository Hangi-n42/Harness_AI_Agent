"""governance.py — lightweight governance layer.

Two mechanisms, deliberately small and independently testable:

* ``AuditLog``  — append-only, structured audit trail.  It records *metadata*
  only (request id, role, skill, status, duration).  User message text is
  intentionally never written, so no sensitive content is persisted.
* ``PermissionPolicy`` — a simple role → allowed-skills table (RBAC).  The
  default policy lets every role use every public skill; restricted policies
  can be injected for tests or future admin-only skills.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path


class AuditLog:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else None
        self._lock = threading.Lock()
        self._memory: list[dict] = []  # always buffered so tests can inspect it

    def audit(self, **fields) -> dict:
        record = {"ts": round(time.time(), 3), **fields}
        if self.path:
            with self._lock:
                with open(self.path, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._memory.append(record)
        return record

    def entries(self) -> list[dict]:
        return list(self._memory)


class PermissionPolicy:
    PUBLIC_SKILLS = ("campus", "library", "translation", "summary", "fallback")
    ROLES = ("guest", "member", "administrator")

    def __init__(self, rules: dict[str, set[str]] | None = None):
        # Default: every role may use every public skill.  Pass `rules` to
        # restrict a role (e.g. drop "translation" from "guest").
        self.rules = rules or {
            role: set(self.PUBLIC_SKILLS) for role in self.ROLES
        }

    def authorize(self, role: str, skill_name: str) -> bool:
        return skill_name in self.rules.get(role, set())
