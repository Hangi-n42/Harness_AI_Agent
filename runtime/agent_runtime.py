import time
import uuid


class AgentRuntime:
    def __init__(self, router, guardrail=None, logger=None):
        self.router = router
        self.guardrail = guardrail
        self.logger = logger

    def run(self, message, user="guest"):
        start = time.time()
        request_id = str(uuid.uuid4())[:8]

        # 1. 检查输入
        if not isinstance(message, str) or not message.strip():
            return {
                "request_id": request_id,
                "skill": None,
                "status": "error",
                "response": "请输入有效的问题。",
                "duration": 0
            }

        message = message.strip()

        # 2. 安全检查
        if self.guardrail is not None:
            allowed, reason = self.guardrail.check(message)

            if not allowed:
                result = {
                    "request_id": request_id,
                    "skill": None,
                    "status": "blocked",
                    "response": reason,
                    "duration": round(time.time() - start, 3)
                }

                self.write_log(user, result)
                return result

        # 3. 选择 Skill
        skill = self.router.select(message)

        if skill is None:
            result = {
                "request_id": request_id,
                "skill": None,
                "status": "unmatched",
                "response": "暂时无法匹配合适的功能。",
                "duration": round(time.time() - start, 3)
            }

            self.write_log(user, result)
            return result

        # 4. 执行 Skill
        try:
            answer = skill.execute(message)

            status = "success"

            if skill.name == "fallback":
                status = "unmatched"

            result = {
                "request_id": request_id,
                "skill": skill.name,
                "status": status,
                "response": answer,
                "duration": round(time.time() - start, 3)
            }

        except Exception as e:
            result = {
                "request_id": request_id,
                "skill": getattr(skill, "name", None),
                "status": "failed",
                "response": "该功能执行失败，请稍后重试。",
                "duration": round(time.time() - start, 3)
            }

            print("Runtime error:", e)

        # 5. 写入日志
        self.write_log(user, result)

        return result

    def write_log(self, user, result):
        if self.logger is not None:
            self.logger.write(
                user=user,
                skill=result.get("skill"),
                status=result.get("status"),
                duration=result.get("duration")
            )