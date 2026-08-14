"""Append-only audit logger — one JSON line per request, no message content."""

from __future__ import annotations

import json

from paths import AUDIT_PATH


class AuditLogger:
    def write(self, user: str, skill: str | None, status: str, duration: float) -> None:
        record = {"user": user, "skill": skill, "status": status, "duration": duration}
        with AUDIT_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
