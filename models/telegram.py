# This file describes objects from Telegram Bot API.
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
        self.message_id: int = obj.get('message_id', None)
        self.text: str = obj.get('text', None)
        self.chat: Chat = Chat(obj.get('chat', None))

        entities = obj.get('entities', [])
        self.entities: list[Entity] = [Entity(i) for i in entities]


# TODO test all cases of updates: editing of messages, load pictures, music, emoji and etc.
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

    @property
    def last_update_id(self):
        if self.result:
            return self.result[-1].update_id

    @property
    def correct_messages(self) -> list[Message]:
        if not self.result:
            return []

        result = []

        for update in self.result:
            if update.message\
                    and update.message.text\
                    and update.message.chat:
                result.append(update.message)

        return result
