# This file describes models that sends to rabbitmq and gets from it.
# Therefore, poller will send messages and may be some other entities
# to rabbitmq and worker will get these entities from rabbitmq too
import msgpack


class RabbitMessage:
    def __init__(self, text=None, chat_id=None, bin_data=None):
        if bin_data:
            message_dict = msgpack.unpackb(bin_data)
            self.text = message_dict['text']
            self.chat_id = message_dict['chat_id']
        elif text and chat_id:
            self.text = text
            self.chat_id = chat_id
        else:
            raise TypeError('init must accept bin_data or text and chat_id')

    def to_bin(self):
        return msgpack.packb(self.__dict__)
