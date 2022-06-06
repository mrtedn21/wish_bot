# This file describes models that sends to rabbitmq and gets from it.
# Therefore, poller will send messages and may be some other entities
# to rabbitmq and worker will get these entities from rabbitmq too
import msgpack


class RabbitMessage:
    def __init__(self,
                 text: str = None,
                 chat_id: int = None,
                 username: str = None,
                 bin_data: bin = None) -> None:
        if bin_data:
            message_dict = msgpack.unpackb(bin_data)
            self.text = message_dict['text']
            self.chat_id = message_dict['chat_id']
            # I don't store user_id in the model because there are not
            # user_id in telegram api response. And it isn't must have,
            # because chat_id is enough
            self.username = message_dict['username']
        elif text and chat_id:
            self.text = text
            self.chat_id = chat_id
            self.username = username
        else:
            raise TypeError('init must accept bin_data or text and chat_id')

    def to_bin(self) -> bytes:
        return msgpack.packb(self.__dict__)
