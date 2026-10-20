import httpx

r = httpx.get("https://httpbin.org/get", params={"q": "test"}, timeout=30)
print("状态码：", r.status_code)
print("参数：", r.json()["args"])

r = httpx.post("https://httpbin.org/post", json={"name": "测试"}, timeout=30)
print("发送的数据：", r.json()["json"])