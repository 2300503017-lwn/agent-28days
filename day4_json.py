import httpx
from pydantic import BaseModel, Field
from pydantic import ValidationError

#pydantic 不仅能检查类型，还能检查取值范围，就像接口测试中的字段断言。


URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:3b"

class BugReport(BaseModel):
    title: str
    severity: int = Field(ge=1, le=4)  #Field(ge=1, le=4)，意思是 severity 必须大于等于 1 且小于等于 4，
    steps: list[str]

SYSTEM = """你是缺陷报告助手。把用户的描述整理成 JSON，只输出 JSON，不要任何其他文字。
格式：{"title": "简短标题", "severity": 1到4的整数, "steps": ["步骤1", "步骤2"]}"""

BUG = "点击登录按钮后页面一直转圈，等了一分钟也没反应，换浏览器也一样"

def ask(text):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}]
    r = httpx.post(URL, json={"model": MODEL, "messages": messages, "stream": False,"format": BugReport.model_json_schema()}, timeout=120)
    return r.json()["message"]["content"]
    # 强制转换Json格式 "format": BugReport.model_json_schema(),
    # BugReport.model_json_schema() 会把pydantic 类自动转换成一份标准的 JSON 结构描述，
    # 如果不加就会失败，模型返回的文本不是合法的 JSON
    # 加上之后，Ollama 会强制模型只输出符合结构的 JSON
ok = 0
for i in range(10):
    raw = ask(BUG)
    try:
        print("模型原始输出：", raw)
        report=BugReport.model_validate_json(raw)
        print("校验通过：", report)     
        #model_validate_json，它一步完成"把文本解析成 JSON"和"按 BugReport 的规则校验"两件事，任何一步不通过都会报错。
        ok += 1
    except ValidationError:
        print(f"第{i+1}次失败，原始输出：{raw[:100]}")
print(f"成功率：{ok}/10")
