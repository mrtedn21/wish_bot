import aiohttp
import asyncio
from msgpack import packb
from pika import BlockingConnection
from pika import ConnectionParameters

from poller.api_functions import get_updates
from poller.api_functions import send_message

connection = BlockingConnection(ConnectionParameters('localhost'))
channel = connection.channel()
QUEUE_NAME = 'wish'
channel.queue_declare(queue=QUEUE_NAME)


async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            response = await get_updates(session)
            if response:
                for update in response.result:
                    await send_message(session, update.message.chat.id, update.message.text)
                    channel.basic_publish(
                        exchange='',
                        routing_key=QUEUE_NAME,
                        body=packb({'message': update.message.text})
                    )
                    # TODO make checking if result of sending message is ok


asyncio.run(main())
