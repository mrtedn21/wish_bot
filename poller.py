import asyncio
import logging

import aiohttp
from aio_pika import Message
from aio_pika import connect_robust

from api_functions import get_updates
from models.rabbit import RabbitMessage
from models.telegram import ApiResponse

QUEUE_NAME = 'wish'


async def main() -> None:
    connection = await connect_robust(host='localhost')
    update_id = None
    logging.basicConfig(
        filename='poller.log',
        encoding='utf-8',
        level=logging.DEBUG)

    async with aiohttp.ClientSession() as session, connection:
        channel = await connection.channel()
        await channel.declare_queue(QUEUE_NAME)

        while True:
            try:
                raw_response = await get_updates(session, update_id)
                response = ApiResponse(raw_response)
                update_id = response.last_update_id
            except BaseException:
                logging.error(f'Error whlie response handle. '
                              f'Raw response: "{raw_response}"')
                print(raw_response)

            for message in response.correct_messages:
                rb_message = RabbitMessage(
                    chat_id=message.chat.id,
                    text=message.text,
                    username=message.chat.username,
                )

                await channel.default_exchange.publish(
                    Message(rb_message.to_bin()),
                    routing_key=QUEUE_NAME,
                )
                # TODO make checking if result of sending message is ok


if __name__ == '__main__':
    asyncio.run(main())
