import asyncio, time

async def fake_call(i):
    await asyncio.sleep(1)
    return f"请求{i}完成"

async def main():
    start = time.time()
    for i in range(5):
        print(await fake_call(i))
    print(f"串行耗时 {time.time() - start:.1f} 秒")

asyncio.run(main())