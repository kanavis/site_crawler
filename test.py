#!/usr/bin/env python
import asyncio
import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://bbc.com') as resp:
            print(await resp.text())


asyncio.run(main())
