from pathlib import Path

import aiohttp

from models import ApiResponse

with open(Path(__file__).parent / 'token', 'r') as f:
    token = f.read()

base_url = f'https://api.telegram.org/{token}'
update_id = None


async def get_updates(session: aiohttp.ClientSession):
    global update_id
    timeout_param = 'timeout=60'
    function_url = f'{base_url}/getUpdates?{timeout_param}'
    if update_id:
        offset_param = f'offset={update_id + 1}'
        function_url = f'{function_url}&{offset_param}'

    async with session.get(function_url) as res:
        obj = await res.json()
        response = ApiResponse(obj)
        if response.result:
            update_id = response.last_update_id()
            return response
        return None


async def send_message(session: aiohttp.ClientSession, chat_id: int, text: str):
    chat_id_param = f'chat_id={chat_id}'
    text_param = f'text={text}'
    function_url = f'{base_url}/sendMessage?{chat_id_param}&{text_param}'
    async with session.get(function_url) as res:
        obj = await res.json()
