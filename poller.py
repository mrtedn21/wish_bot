import asyncio

import aiohttp
from aio_pika import Message
from aio_pika import connect_robust

from api_functions import get_updates
from models.rabbit import RabbitMessage

QUEUE_NAME = 'wish'


async def main() -> None:
    connection = await connect_robust(host='localhost')

    async with aiohttp.ClientSession() as session, connection:
        channel = await connection.channel()
        await channel.declare_queue(QUEUE_NAME)

        while True:
            response = await get_updates(session)
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
