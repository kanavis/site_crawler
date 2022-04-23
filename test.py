#!/usr/bin/env python
import asyncio


async def sleep_print(x):
    await asyncio.sleep(1)
    print('aaa {}'.format(x))
    return x + 1


async def main():
    res = await asyncio.wait([
        asyncio.create_task(sleep_print(x))
        for x in range(5)
    ])
    print(res for res[0])

asyncio.run(main())
