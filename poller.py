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
    connection = await connect_robust(host='rabbit')
    update_id = None
    logging.basicConfig(
        filename='logs/poller.log',
        level=logging.DEBUG)

    async with aiohttp.ClientSession() as session, connection:
        channel = await connection.channel()
        await channel.declare_queue(QUEUE_NAME)

        while True:
            try:
                raw_response = await get_updates(session, update_id)
                response = ApiResponse(raw_response)
                update_id = response.last_update_id
            except BaseException as e:
                logging.error(f'Error whlie response handle. '
                              f'Raw response: "{raw_response}"')
                logging.error(str(e))
                print(raw_response)
                # This needs because creating of ApiResponse crashes sometimes with
                # incorrectly commands. This must bugs must be fixed in the future,
                # but at moment bot must work and only pass this incorrectly command
                # and log details about it to fix this bug
                update_id = raw_response['result'][-1]['update_id']
                continue

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


if __name__ == '__main__':
    asyncio.run(main())
