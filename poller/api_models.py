# There are models in this file that describes objects from Telegram
# Bot API. There are only objects that needs for this app. And fields
# of these models are only that needs for this app too. Therefore,
# original API has more models and fields


class Entity:
    def __init__(self, obj):
        self.type = obj['type']


class Message:
    def __init__(self, obj):
        self.message_id: int = obj['message_id']
        self.text: str = obj['text']

        entities = obj.get('entities', [])
        self.entities: list[Entity] = [Entity(i) for i in entities]


class ApiUpdate:
    def __init__(self, obj):
        self.update_id: int = int(obj['update_id'])
        self.message: Message = Message(obj['message'])


class ApiResponse:
    def __init__(self, obj):
        self.ok: str = obj['ok']
        self.result: list[ApiUpdate] = [ApiUpdate(i) for i in obj['result']]
