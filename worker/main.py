from msgpack import unpackb
from pika import BlockingConnection
from pika import ConnectionParameters

connection = BlockingConnection(ConnectionParameters('localhost'))
channel = connection.channel()
QUEUE_NAME = 'wish'
channel.queue_declare(queue=QUEUE_NAME)


def callback(ch, method, properties, body):
    print(unpackb(body))


channel.basic_consume(
    queue=QUEUE_NAME,
    auto_ack=True,
    on_message_callback=callback
)

channel.start_consuming()
