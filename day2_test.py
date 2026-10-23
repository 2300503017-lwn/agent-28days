import asyncio, time
import httpx

async def serial(client):
    start = time.time()
    for i in range(5):
      results=await client.get("https://httpbin.org/delay/1")
      print(f"串行 第{i + 1}个：{results.status_code}")
    return time.time() - start

async def concurrent(client):
    start = time.time()
    tasks = [client.get("https://httpbin.org/delay/1") for _ in range(5)]
    responses = await asyncio.gather(*tasks)
    print("并发结果：",[r.status_code for r in responses])
    return time.time() - start  

async def main():
    async with httpx.AsyncClient(timeout=120) as client:
        t1 = await serial(client)
        t2 = await concurrent(client)
    print(f"串行耗时：{t1:.1f} 秒")
    print(f"并发耗时：{t2:.1f} 秒")
    print(f"提速：{t1 / t2:.1f} 倍")


asyncio.run(main())

#对比两种耗时 串行 5.1秒    并行1.0秒