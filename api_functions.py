import os

import aiohttp

token = os.environ['TELEGRAM_BOT_TOKEN']
base_url = f'https://api.telegram.org/{token}'


async def get_updates(session: aiohttp.ClientSession, update_id: int) -> dict:
    timeout_param = 'timeout=60'
    function_url = f'{base_url}/getUpdates?{timeout_param}'
    if update_id:
        offset_param = f'offset={update_id + 1}'
        function_url = f'{function_url}&{offset_param}'

    async with session.get(function_url) as res:
        return await res.json()


async def send_message(session: aiohttp.ClientSession, chat_id: int, text: str) -> None:
    chat_id_param = f'chat_id={chat_id}'
    text_param = f'text={text}'
    function_url = f'{base_url}/sendMessage?{chat_id_param}&{text_param}'
    await session.get(function_url)
