from pydantic import BaseModel, ValidationError

class BugReport(BaseModel):
    title: str
    severity: int
    steps: list[str]

report = BugReport(title="登录失败", severity="2", steps=["打开页面", "点击登录"])
print(report)
print(report.severity + 1)

try:
    BugReport(title="登录失败", severity="高", steps=[])
except ValidationError as e:
    print("校验失败：", e)