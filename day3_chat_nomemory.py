import httpx

URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:3b"

messages = [{"role": "system", "content": "你是一个耐心的软件测试导师，回答简洁。"}]

while True:
    user_input = input("你：")
    if user_input == "退出":
        break
    messages = [{"role": "system", "content": "你是一个耐心的软件测试导师，回答简洁。"},
                {"role": "user", "content": user_input}
                ]
    #messages.append({"role": "user", "content": user_input})#
    r = httpx.post(URL, json={"model": MODEL, "messages": messages, "stream": False}, timeout=120)
    reply = r.json()["message"]["content"]
    print("AI：", reply)
    messages.append({"role": "assistant", "content": reply}) 