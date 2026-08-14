"""library.py — SZU library branches and official address.

This skill's knowledge is narrow and enumerable (two fields), so it uses a
*strict* deterministic gate: only branch/address questions are answerable,
anything else returns "unavailable" without consulting the model.
"""

from __future__ import annotations

from skills.base import KnowledgeSkill


class LibrarySkill(KnowledgeSkill):
    name = "library"
    description = "SZU library: branch locations and the official address."
    keywords = ("图书馆", "library", "分馆", "branch", "branches", "address", "地址", "在哪", "哪里")
    facts_key = "library"

    FIELD_KEYWORDS = {
        "main_branches": ("branch", "branches", "分馆", "有哪些", "几个", "which", "list", "北馆", "南馆", "central"),
        "official_address": ("address", "地址", "where", "在哪", "位置", "location", "哪里"),
    }

    def match_facts(self, text: str) -> dict | None:
        low = text.lower()
        lib = self.knowledge()
        selected = {}
        for field, kws in self.FIELD_KEYWORDS.items():
            if any(k in low for k in kws):
                selected[field] = lib[field]
        # Strict gate: no field matched -> not answerable -> unavailable.
        return selected or None
