import time
import asyncio


async def do_nothing():
    while True:

        try:
            print("123456")
        except Exception as e:
            print(e)

        await asyncio.sleep(1)


async def init():
    """
        定时任务
    """
    await asyncio.gather(
        do_nothing(),
    )
