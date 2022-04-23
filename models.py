# First part of this file describes models for app self
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


# Second part of this file describes objects from Telegram Bot API.
# There are only objects that needs for this app. And fields
# of these models are only that needs for this app too. Therefore,
# original API has more models and fields


class Entity:
    def __init__(self, obj):
        self.type = obj['type']


class Chat:
    def __init__(self, obj):
        self.id: int = obj['id']
        self.username: str = obj['username']
        self.type: str = obj['type']
        self.first_name: str = obj.get('first_name', None)
        self.last_name: str = obj.get('last_name', None)


class Message:
    def __init__(self, obj):
        self.message_id: int = obj['message_id']
        self.text: str = obj['text']
        self.chat: Chat = Chat(obj['chat'])

        entities = obj.get('entities', [])
        self.entities: list[Entity] = [Entity(i) for i in entities]


class ApiUpdate:
    def __init__(self, obj):
        self.update_id: int = int(obj['update_id'])
        self.message: Message = Message(obj['message'])


class ApiResponse:
    def __init__(self, obj):
        self.ok: str = obj['ok']
        if obj.get('result', []):
            self.result: list[ApiUpdate] = [ApiUpdate(i) for i in obj['result']]
        else:
            self.result = None

    def last_update_id(self):
        if self.result:
            return self.result[-1].update_id
