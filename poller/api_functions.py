from pathlib import Path

import aiohttp

with open(Path(__file__).parent / 'token', 'r') as f:
    token = f.read()

base_url = f'https://api.telegram.org/{token}'


async def get_updates(session: aiohttp.ClientSession):
    timeout_parameter = 'timeout=60'
    function_url = f'{base_url}/getUpdates?{timeout_parameter}'

    async with session.get(function_url) as res:
        return await res.json()
