import aiohttp
import asyncio

from poller.api_functions import get_updates


async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            await get_updates(session)


asyncio.run(main())
