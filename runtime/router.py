class SkillRouter:
    def __init__(self, skills):
        self.skills = skills

    def select(self, message):
        text = message.lower().strip()

        # 1. 翻译类问题
        words = [
            "translate", "translation",
            "翻译", "译成", "中文", "英文"
        ]

        if any(w in text for w in words):
            return self.skills.get("translation")

        # 2. 图书馆类问题
        words = [
            "library", "book", "borrow", "return book",
            "图书馆", "借书", "还书", "开放时间"
        ]

        if any(w in text for w in words):
            return self.skills.get("library")

        # 3. 校园信息类问题
        words = [
            "shenzhen university", "szu", "campus",
            "motto", "founded", "president",
            "深圳大学", "深大", "校训",
            "成立", "创办", "校区", "校长"
        ]

        if any(w in text for w in words):
            return self.skills.get("campus")

        # 4. 无法匹配时使用 fallback
        return self.skills.get("fallback")