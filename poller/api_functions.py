from pathlib import Path

import aiohttp

from poller.api_models import ApiResponse

with open(Path(__file__).parent / 'token', 'r') as f:
    token = f.read()

base_url = f'https://api.telegram.org/{token}'
update_id = None


async def get_updates(session: aiohttp.ClientSession):
    global update_id
    timeout_parameter = 'timeout=60'
    function_url = f'{base_url}/getUpdates?{timeout_parameter}'
    if update_id:
        offset_parameter = f'offset={update_id + 1}'
        function_url = f'{function_url}&{offset_parameter}'

    async with session.get(function_url) as res:
        obj = await res.json()
        response = ApiResponse(obj)
        if response.result:
            for update in response.result:
                print(await res.text())
                print(update.message.text)

        update_id = response.last_update_id()
