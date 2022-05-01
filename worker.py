import asyncio

import aiohttp
from aio_pika import connect_robust

from api_functions import send_message
from models.database import engine
from models.rabbit import RabbitMessage
from services import create_wish


QUEUE_NAME = 'wish'


async def main() -> None:
    connection = await connect_robust(host='localhost')

    async with aiohttp.ClientSession() as session, connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(QUEUE_NAME)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    rb_message = RabbitMessage(bin_data=message.body)
                    print(rb_message.text)
                    await send_message(
                        session=session,
                        chat_id=rb_message.chat_id,
                        text=rb_message.text
                    )
                    await create_wish('test', rb_message.text)

    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main())
