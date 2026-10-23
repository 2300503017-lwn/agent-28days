import httpx, difflib
from collections import Counter

URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:3b"
RUNS = 10

INPUTS = {
    "分类题": "这个缺陷的严重程度是1到4的哪一级？只回答一个数字。缺陷：点击登录按钮后页面一直转圈，无法登录。",
    "开放题": "用一句话解释什么是回归测试。",
}

def ask(prompt, temperature):
    r = httpx.post(URL, json={
        "model": MODEL, "stream": False,
        "messages": [{"role": "user", "content": prompt}],
        "options": {"temperature": temperature},
    }, timeout=120)
    return r.json()["message"]["content"].strip()

def avg_similarity(outputs):
    pairs = [(a, b) for i, a in enumerate(outputs) for b in outputs[i + 1:]]
    return sum(difflib.SequenceMatcher(None, a, b).ratio() for a, b in pairs) / len(pairs)

rows, log = [], []
for name, prompt in INPUTS.items():
    for t in (0, 1):
        outputs = [ask(prompt, t) for _ in range(RUNS)]
        top_count = Counter(outputs).most_common(1)[0][1]
        lengths = [len(o) for o in outputs]
        rows.append((name, t, len(set(outputs)), top_count, min(lengths), max(lengths), avg_similarity(outputs)))
        log.append(f"===== {name} temperature={t} =====\n" + "\n".join(outputs))
        print(f"{name} temperature={t} 完成")

with open("day5_outputs.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(log))

print("\n| 输入 | temperature | 不同输出数 | 最常见输出次数 | 最短 | 最长 | 平均相似度 |")
print("|---|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]}/10 | {r[4]} | {r[5]} | {r[6]:.2f} |")