"""campus.py — Shenzhen University facts (name, motto, year, campuses)."""

from __future__ import annotations

from skills.base import KnowledgeSkill


class CampusSkill(KnowledgeSkill):
    name = "campus"
    description = "Shenzhen University facts: name, motto, founding year, campuses."
    keywords = (
        "深圳大学", "深大", "szu", "university", "motto", "校训", "established",
        "建校", "成立", "校区", "campus", "简称", "缩写", "abbreviation", "大学", "学校",
    )
    facts_key = "university"

    # field -> keywords that indicate the user is asking about that field
    FIELD_KEYWORDS = {
        "name": ("name", "名称", "全称", "叫什么名字", "叫什么", "英文名"),
        "abbreviation": ("abbreviation", "简称", "缩写", "szu"),
        "established": ("established", "建校", "成立", "founded", "创办", "哪一年", "年份", "什么时候建", "year"),
        "motto": ("motto", "校训"),
        "campuses": ("campus", "校区", "校园", "campuses", "几个校区"),
    }
    # a bare mention of the university -> give the whole overview object
    OVERVIEW_KEYWORDS = ("深圳大学", "深大", "szu", "university", "大学", "学校", "介绍", "about")

    def match_facts(self, text: str) -> dict | None:
        low = text.lower()
        uni = self.knowledge()
        selected = {}
        for field, kws in self.FIELD_KEYWORDS.items():
            if any(k in low for k in kws):
                selected[field] = uni[field]
        if selected:
            return selected
        if any(k in low for k in self.OVERVIEW_KEYWORDS):
            return uni
        return None
