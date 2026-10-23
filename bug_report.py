"""
缺陷报告生成器（第 6 天项目）
把口语化的 bug 描述整理成结构化缺陷报告，同时输出 JSON 和 Markdown 两个文件。

用法：
  python bug_report.py "点击登录按钮后页面一直转圈"     直接传入描述
  python bug_report.py -f bug.txt                       从文本文件读取描述
  python bug_report.py                                  不带参数，进入交互输入
  python bug_report.py "描述" --mock                    不调用模型，用假数据测试整个流程
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import httpx
from pydantic import BaseModel, Field, ValidationError

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "qwen2.5:3b"
MAX_RETRIES = 3
SEVERITY_LABELS = {1: "致命", 2: "严重", 3: "一般", 4: "轻微"}


# ---------- 1. 数据结构：报告必须长什么样（第 2、4 天学的 pydantic） ----------
class BugReport(BaseModel):
    title: str = Field(min_length=4, max_length=40, description="一句话标题")
    module: str = Field(description="所属功能模块，无法判断时填“未提供”")
    severity: int = Field(ge=1, le=4, description="严重程度，1 最严重")
    steps: list[str] = Field(min_length=1, description="复现步骤，按顺序排列")
    expected: str = Field(description="预期结果")
    actual: str = Field(description="实际结果")
    environment: str = Field(description="环境信息，描述中没有则填“未提供”")


# ---------- 2. 给模型的规则（第 3 天学的 system prompt） ----------
SYSTEM_PROMPT = """你是一名资深测试工程师，负责把口语化的缺陷描述整理成规范的缺陷报告。
规则：
1. 只输出 JSON，不要输出任何其他文字。
2. 只使用描述中给出的信息，不要编造。描述里没有提到的环境、模块等信息，填写"未提供"。
3. 严重程度：1=致命（崩溃、数据丢失、核心功能完全不可用），2=严重（主要功能受影响），3=一般（次要功能问题），4=轻微（界面、文案等）。
4. 标题简洁，不超过 40 个字。复现步骤按顺序拆分，每步一句话。"""


# ---------- 3. 调用模型 ----------
def call_ollama(messages, model):
    """调用本地 Ollama。用 format 强制 JSON 结构，temperature=0 让结果更稳定（第 4、5 天）。"""
    try:
        r = httpx.post(OLLAMA_URL, json={
            "model": model,
            "messages": messages,
            "stream": False,
            "format": BugReport.model_json_schema(),
            "options": {"temperature": 0},
        }, timeout=180)
        r.raise_for_status()
    except httpx.ConnectError:
        sys.exit("错误：无法连接 Ollama。请确认 Ollama 已启动（可以先运行 ollama list 检查）。")
    except httpx.TimeoutException:
        sys.exit("错误：模型响应超时。本地模型较慢，可以稍后重试，或换一个更小的模型。")
    except httpx.HTTPStatusError as e:
        sys.exit(f"错误：Ollama 返回 {e.response.status_code}：{e.response.text}")
    return r.json()["message"]["content"]


def call_mock(messages, model):
    """假模型（Mock）：第一次故意返回不合格内容，第二次返回合格 JSON，用来验证重试流程。"""
    attempts = sum(1 for m in messages if m["role"] == "assistant")
    if attempts == 0:
        return '好的，以下是缺陷报告：{"title": "登录"}'
    return json.dumps({
        "title": "点击登录按钮后页面持续加载无响应",
        "module": "登录",
        "severity": 1,
        "steps": ["打开登录页面", "输入账号和密码", "点击登录按钮"],
        "expected": "登录成功并跳转到首页",
        "actual": "页面一直显示加载中，超过一分钟无响应",
        "environment": "未提供",
    }, ensure_ascii=False)


# ---------- 4. 生成报告：清洗 + 校验 + 带反馈的重试（第 4 天） ----------
def extract_json(raw):
    """只保留第一个 { 到最后一个 } 之间的内容，去掉模型多说的废话。"""
    start, end = raw.find("{"), raw.rfind("}")
    return raw[start:end + 1] if start != -1 and end != -1 else raw


def generate_report(description, chat_fn, model):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"缺陷描述：{description}"},
    ]
    for attempt in range(1, MAX_RETRIES + 1):
        raw = chat_fn(messages, model)
        try:
            report = BugReport.model_validate_json(extract_json(raw))
            print(f"[第 {attempt} 次生成] 校验通过")
            return report
        except ValidationError as e:
            print(f"[第 {attempt} 次生成] 校验失败：{e.errors()[0]['msg']}")
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": f"输出不符合要求，错误信息如下：\n{e}\n请修正后重新输出，只输出 JSON。"})
    sys.exit(f"错误：重试 {MAX_RETRIES} 次后仍未生成合格的报告，请把描述写得更具体一些再试。")


# ---------- 5. 输出：Markdown 渲染与保存文件 ----------
def to_markdown(report, description):
    steps = "\n".join(f"{i}. {s}" for i, s in enumerate(report.steps, 1))
    quoted = description.replace("\n", "\n> ")
    return f"""# {report.title}

| 字段 | 内容 |
|---|---|
| 所属模块 | {report.module} |
| 严重程度 | S{report.severity}（{SEVERITY_LABELS[report.severity]}） |
| 环境 | {report.environment} |

## 复现步骤

{steps}

## 预期结果

{report.expected}

## 实际结果

{report.actual}

## 原始描述

> {quoted}
"""


def save(report, description, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out / f"bug_{stamp}.json"
    md_path = out / f"bug_{stamp}.md"
    json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    md_path.write_text(to_markdown(report, description), encoding="utf-8")
    return json_path, md_path


# ---------- 6. 命令行入口 ----------
def read_description(args):
    if args.file:
        return Path(args.file).read_text(encoding="utf-8").strip()
    if args.description is not None:
        return args.description.strip()
    print("请输入缺陷描述（输入完成后按回车）：")
    return input("> ").strip()


def main():
    parser = argparse.ArgumentParser(description="把 bug 描述整理成结构化缺陷报告（JSON + Markdown）")
    parser.add_argument("description", nargs="?", help="缺陷描述文本")
    parser.add_argument("-f", "--file", help="从文本文件读取缺陷描述")
    parser.add_argument("-o", "--out", default="reports", help="输出文件夹，默认 reports")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, help=f"Ollama 模型名，默认 {DEFAULT_MODEL}")
    parser.add_argument("--mock", action="store_true", help="不调用模型，用假数据测试流程")
    args = parser.parse_args()

    description = read_description(args)
    if not description:
        sys.exit("错误：缺陷描述不能为空。")

    chat_fn = call_mock if args.mock else call_ollama
    print(f"正在生成报告（模型：{'Mock' if args.mock else args.model}）……")
    report = generate_report(description, chat_fn, args.model)

    json_path, md_path = save(report, description, args.out)
    print("\n" + to_markdown(report, description))
    print(f"已保存：{json_path}")
    print(f"已保存：{md_path}")


if __name__ == "__main__":
    main()