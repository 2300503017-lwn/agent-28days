import httpx

URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:3b"
QUESTION = "如何测试一个登录功能？"

PROMPTS = {
    "默认": "你是一个助手。",
    "资深测试": "你是有10年经验的测试专家，按正常、异常、边界、安全四类列出测试点。",
    "极简": "你只用大于40，小于50个字回答。",
}
#提示词：  "极简": "你只用不超过50个字回答。",很难执行 #
for name, system in PROMPTS.items():
    messages = [{"role": "system", "content": system}, {"role": "user", "content": QUESTION}]
    r = httpx.post(URL, json={"model": MODEL, "messages": messages, "stream": False}, timeout=120)
    print(f"===== {name} =====")
    print(r.json()["message"]["content"], "\n")
