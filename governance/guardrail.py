class Guardrail:
    def __init__(self):
        self.blocked_words = [
            "ignore previous instructions",
            "ignore all instructions",
            "show private data",
            "reveal system prompt",
            "忽略之前的指令",
            "忽略所有指令",
            "显示私人数据",
            "泄露系统提示词"
        ]

    def check(self, message):
        text = message.lower()

        for word in self.blocked_words:
            if word in text:
                return (
                    False,
                    "该请求可能包含提示词注入或不安全内容，已被系统阻止。"
                )

        return True, ""