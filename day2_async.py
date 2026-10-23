import asyncio, time

async def fake_call(i):
    await asyncio.sleep(1)
    return f"请求{i}完成"

async def main():
    start = time.time()

    #串行耗时如下
    #for i in range(5):
    #    print(await fake_call(i))
    #print(f"串行耗时 {time.time() - start:.1f} 秒")


    #并行耗时如下
    results=await asyncio.gather(*(fake_call(i) for i in range(5)))
    print(results)
    print(f"并发耗时{time.time()-start:.1f}秒")

asyncio.run(main())

#对比两种耗时 串行 5.1秒    并行1.0秒