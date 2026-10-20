import httpx
from pydantic import BaseModel, Field, ValidationError

URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:3b"

class BugReport(BaseModel):
    title: str
    severity: int = Field(ge=1, le=4)
    steps: list[str] = Field(min_length=5)

SYSTEM = """你是缺陷报告助手。把用户的描述整理成 JSON，只输出 JSON，不要任何其他文字。
格式：{"title": "简短标题", "severity": 1到4的整数, "steps": ["步骤1", "步骤2"]}"""

BUG = "点击登录按钮后页面一直转圈，等了一分钟也没反应，换浏览器也一样"

def chat(messages):
    r = httpx.post(URL, json={"model": MODEL, "messages": messages, "stream": False}, timeout=120)
    return r.json()["message"]["content"]

def clean(raw):
    start, end = raw.find("{"), raw.rfind("}")
    return raw[start:end + 1]

def get_report(text, chat_fn=chat, max_retries=4):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}]
    for attempt in range(1, max_retries + 1):
        raw = chat_fn(messages)
        try:
            report = BugReport.model_validate_json(clean(raw))
            print(f"第{attempt}次尝试：成功")
            return report
        except ValidationError as e:
            print(f"第{attempt}次尝试：失败，原因：{e.errors()[0]['msg']}")
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": f"你的输出不符合要求，错误信息如下：\n{e}\n请修正后重新输出，只输出 JSON。"})
    raise RuntimeError(f"重试 {max_retries} 次后仍然失败")

try:
    report = get_report(BUG)
    print("最终结果：", report)
except RuntimeError as e:
    print("生成失败：", e)

#核心是 get_report 函数里的循环，最多尝试 3 次。
# 每次拿到模型输出后先清洗、再校验：成功就直接返回结果；
# 失败就把模型这次的错误输出和pydantic 的具体错误信息一起追加到对话记录里，再让模型重新生成。
# 这里用到了第 3 天学的多轮对话：模型能看到"自己上次写了什么"和"错在哪里"，所以第二次往往能改对。
# 3 次都失败，就抛出错误，由最下面的 try/except 给出一条清楚的提示，而不是让程序直接崩溃。#

# steps 那一行加了 Field(min_length=5)，要求至少 5 个步骤，但 system prompt 里故意没提这个要求。
# 所以模型第一次大概率只写两三个步骤，校验失败；然后它会看到错误信息里说"至少需要 5 项"，第二次就会补足。
# 看到"失败后重试并成功"，就证明错误反馈机制生效了


#测一个"永远失败"的场景
def fake_chat(messages):
    return "抱歉，我无法输出 JSON"
try:
    get_report(BUG, chat_fn=fake_chat)
except RuntimeError as e:
    print("生成失败：", e)


#Mock，也就是用一个假函数代替真的模型
#你再次运行，会看到连续 4 次失败，然后是"生成失败：重试 4 次后仍然失败"。
# 之所以给 get_report 设计一个 chat_fn 参数，就是为了方便这样替换。