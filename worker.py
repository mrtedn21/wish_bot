import asyncio
import logging

import aiohttp
from aio_pika import connect_robust
from sqlalchemy.exc import ProgrammingError

from api_functions import send_message
from models.database import engine
from models.database import main as create_tables
from models.rabbit import RabbitMessage
from services import create_private_user
from services import create_wish
from services import delete_private_user
from services import delete_wish_by_id
from services import get_all_users
from services import get_private_user
from services import get_private_users
from services import get_wishes_by_username

QUEUE_NAME = 'wish'
# usual \n doesn't work in url
NEW_LINE_CHARACTER = '%0A'


class MessageHandler:
    def __init__(
            self,
            session: aiohttp.ClientSession,
            rb_message: RabbitMessage) -> None:
        self.session = session
        self.rb_message = rb_message

    async def handle(self) -> None:
        if not self.rb_message.text.startswith('/') \
                or self.rb_message.text == '/':
            return

        commands = self.rb_message.text[1:].split(' ')
        # remove elements = spaces. Need for case if user will
        # write commands with several spaces between commands
        commands = [command for command in commands if command]
        try:
            first_argument = commands[1]
        except IndexError:
            first_argument = None
        command_name = commands[0].lower()

        if command_name == 'add':
            await self.add_command(
                username=self.rb_message.username,
                wish=' '.join(commands[1:]),
            )
        elif command_name == 'addpw':
            # shortening for add private wish
            await self.add_command(
                username=self.rb_message.username,
                wish=' '.join(commands[1:]),
                private=True
            )
        elif command_name == 'addpu':
            # shortening for add private user
            await self.add_private_user_command(
                username=self.rb_message.username,
                private_username=first_argument,
            )
        elif command_name == 'show':
            await self.show_command(
                sender_of_command=self.rb_message.username,
                owner_of_wishes=first_argument,
            )
        elif command_name == 'showpu':
            await self.show_private_users_command(
                username=self.rb_message.username,
            )
        elif command_name == 'delete':
            await self.delete_command(
                username=self.rb_message.username,
                wish_index=first_argument,
            )
        elif command_name == 'deletepu':
            await self.delete_private_user_command(
                username=self.rb_message.username,
                private_username=first_argument,
            )
        elif command_name == 'showau':
            await self.show_all_users()
        elif command_name == 'help':
            await self.help_command()
        else:
            await self.send_message(f"Command doesn't exist")

    async def send_message(self, text: str) -> None:
        await send_message(
            session=self.session,
            chat_id=self.rb_message.chat_id,
            text=text,
        )

    async def add_command(
            self,
            username: str,
            wish: str,
            private: bool = False) -> None:
        if not wish:
            await self.send_message('You want to add empty wish')
            return

        result_of_creating = await create_wish(
            username=username,
            text=wish,
            private=private
        )
        if result_of_creating:
            await self.send_message('Successfully added')
        else:
            await self.send_message('You already have such wish')

    async def add_private_user_command(
            self,
            username: str,
            private_username: str) -> None:
        await create_private_user(
            username,
            private_username
        )

        await self.send_message(
            f'Private user successfully added'
        )

    async def show_command(
            self,
            sender_of_command: str,
            owner_of_wishes: str) -> None:
        username = owner_of_wishes or sender_of_command

        if sender_of_command == owner_of_wishes or owner_of_wishes is None:
            is_private_user = True
        else:
            is_private_user = await get_private_user(
                owner_of_wishes,
                sender_of_command
            )

        if is_private_user:
            wishes = await get_wishes_by_username(
                username,
                include_private=True
            )
        else:
            wishes = await get_wishes_by_username(username)

        if not wishes:
            await self.send_message(
                f'There are no wishes for user "{username}"'
            )
            return

        indexed_wishes = []
        for index, wish in enumerate(wishes):
            indexed_wishes.append(f'{index}. {wish[1]}')

        result_text = NEW_LINE_CHARACTER.join(indexed_wishes)
        await self.send_message(
            f'Wishes of user "{username}" is:{NEW_LINE_CHARACTER}{result_text}'
        )

    async def show_private_users_command(self, username: str) -> None:
        private_users = await get_private_users(username)
        if not private_users:
            await self.send_message(
                f"You don't have any private users"
            )
            return

        private_users = [f'* {pu[0]}' for pu in private_users]
        private_users_str = NEW_LINE_CHARACTER.join(private_users)

        await self.send_message(
            f'Your private users:{NEW_LINE_CHARACTER}{private_users_str}'
        )

    async def delete_command(self, username: str, wish_index: str) -> None:
        if wish_index.startswith('-'):
            await self.send_message(f'Please, enter positive index')
            return

        try:
            wish_index = int(wish_index)
        except ValueError:
            await self.send_message(f'Please, enter valid index')
            return

        wishes = await get_wishes_by_username(username, include_private=True)
        if len(wishes) <= wish_index:
            await self.send_message(
                f"You want delete wish thad doesn't exists"
            )
            return

        wish_for_deleting = wishes[wish_index]
        await delete_wish_by_id(wish_for_deleting[0])

        await self.send_message(
            f'Successfully delete wish "{wish_for_deleting[1]}"'
        )

    async def delete_private_user_command(
            self,
            username: str,
            private_username: str) -> None:
        await delete_private_user(username, private_username)

        await self.send_message(
            f'Private user "{private_username}" deleted successfully'
        )

    async def show_all_users(self) -> None:
        users = await get_all_users()
        users_strings = [f'* {u[0]}' for u in users]
        result = NEW_LINE_CHARACTER.join(users_strings)

        await self.send_message(result)

    async def help_command(self) -> None:
        await self.send_message(
            f"add - add new wish{NEW_LINE_CHARACTER}"
            f"addpw - add new private wish, that will be seen only"
            f"by users that you add to your private user"
            f"list{NEW_LINE_CHARACTER}"
            f"addpu - add private user to your private user list about"
            f"which wtitten above{NEW_LINE_CHARACTER}"
            f"show - if write only show, without any parameters,"
            f"you will see your wishes. If you will add username"
            f"as parameter, you will see wishes of this user."
            f"If you in his private list, you will see all his wishes."
            f"If there are no you in his private list, you will"
            f"see only his public wishes{NEW_LINE_CHARACTER}"
            f"showpu - show private users, that you"
            f"have added{NEW_LINE_CHARACTER}"
            f"delete - delete wish by index that you see in"
            f"'show' command{NEW_LINE_CHARACTER}"
            f"deletepu - delete user from your"
            f"private list{NEW_LINE_CHARACTER}"
            f"showau - command to show all users in system. "
            f"It's convenient way to remember username"
        )


async def main() -> None:
    try:
        await create_tables()
    except ProgrammingError:
        pass

    connection = await connect_robust(host='rabbit')
    logging.basicConfig(
        filename='logs/worker.log',
        level=logging.DEBUG)

    async with aiohttp.ClientSession() as session, connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(QUEUE_NAME)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    rb_message = RabbitMessage(bin_data=message.body)
                    message_handler = MessageHandler(session, rb_message)
                    try:
                        await message_handler.handle()
                    except BaseException as e:
                        await message_handler.send_message(
                            'You send some strange command'
                        )
                        logging.error(f'Error while message handle. '
                                      f'Message: "{rb_message.text}"')
                        logging.error(str(e))

    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main())
