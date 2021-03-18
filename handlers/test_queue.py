import time
import asyncio
import aiohttp
"""
    适用场景：
        1. 通过回调的方式返回结果，而且处理时间比较长
"""
QUEUE_WORKER = asyncio.Queue()      # asyncio.Queue().maxsize==0 => 不限制大小


async def do(req_data):

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), "req_data:", req_data)

    await QUEUE_WORKER.put(req_data)    # 如果 queue 已经满了，则 等待
    QUEUE_WORKER.put_nowait(req_data)   # 如果 queue 已经满了，则 raise QueueFull

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), "done send.")
    return {"do_not_wait": True}


async def ensure_url_exist(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.head(url) as resp:
                if resp.status >= 300:
                    raise Exception("Status code: %s" % (resp.status))

        except Exception as e:
            raise Exception("Invalid URL: %s, %s" % (url, e))


async def worker():
    """
        工作者的 queue
    """
    while True:
        try:

            req_data = await QUEUE_WORKER.get()
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), "Q.req_data:", req_data)
            await asyncio.sleep(3)
            await ensure_url_exist("https://ayiis.me")

        except Exception as e:
            print(e)
