import aiohttp
import asyncio

from poller.api_functions import get_updates
from poller.api_models import ApiResponse


async def main():
    async with aiohttp.ClientSession() as session:
        res = await get_updates(session)
        response = ApiResponse(res)
        print(res)
        print(response.result[0].message.entities[0].type)


asyncio.run(main())
