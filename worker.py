import asyncio

from msgpack import unpackb
from aio_pika import connect_robust

QUEUE_NAME = 'wish'


async def main() -> None:
    connection = await connect_robust(host='localhost')

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(QUEUE_NAME)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    print(unpackb(message.body))


if __name__ == '__main__':
    asyncio.run(main())
