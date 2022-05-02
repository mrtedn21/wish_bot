import asyncio

import aiohttp
from aio_pika import connect_robust

from api_functions import send_message
from models.database import engine
from models.rabbit import RabbitMessage
from services import create_private_user
from services import create_wish
from services import delete_private_user
from services import delete_wish_by_id
from services import get_private_users
from services import get_wishes_by_username

QUEUE_NAME = 'wish'
# usual \n doesn't work in url
NEW_LINE_CHARACTER = '%0A'


async def add_command(
        chat_id: int,
        username: str,
        wish: str,
        session: aiohttp.ClientSession,
        private: bool = False):
    result_of_creating = await create_wish(
        username=username,
        text=wish,
        private=private
    )
    if result_of_creating:
        await send_message(
            session=session,
            chat_id=chat_id,
            text='successfully added',
        )
    else:
        await send_message(
            session=session,
            chat_id=chat_id,
            text='you already have such wish',
        )


async def add_private_user_command(
        chat_id: int,
        username: str,
        private_username: str,
        session: aiohttp.ClientSession) -> None:
    await create_private_user(
        username,
        private_username
    )

    await send_message(
        session=session,
        chat_id=chat_id,
        text=f'private user successfully added',
    )


async def show_command(
        chat_id: int,
        sender_of_command: str,
        owner_of_wishes: str,
        session: aiohttp.ClientSession) -> None:
    username = owner_of_wishes or sender_of_command
    wishes = await get_wishes_by_username(username)

    if not wishes:
        await send_message(
            session=session,
            chat_id=chat_id,
            text=f'there are no wishes for user "{username}"',
        )
        return

    indexed_wishes = []
    for index, wish in enumerate(wishes):
        indexed_wishes.append(f'{index}. {wish[1]}')

    result_text = NEW_LINE_CHARACTER.join(indexed_wishes)
    await send_message(
        session=session,
        chat_id=chat_id,
        text=f'wishes of user "{username}" is:{NEW_LINE_CHARACTER}{result_text}',
    )


async def show_private_users_command(
        chat_id: int,
        username: str,
        session: aiohttp.ClientSession):
    private_users = await get_private_users(username)
    if not private_users:
        await send_message(
            session=session,
            chat_id=chat_id,
            text=f"you doesn't have any private users",
        )
        return


    private_users = [f'* {pu[0]}' for pu in private_users]
    private_users_str = NEW_LINE_CHARACTER.join(private_users)

    await send_message(
        session=session,
        chat_id=chat_id,
        text=f'your private users:{NEW_LINE_CHARACTER}{private_users_str}',
    )


async def delete_command(
        chat_id: int,
        username: str,
        wish_index: str,
        session: aiohttp.ClientSession):
    # TODO it crashes id delete by not existing index or if there are no wishes at all
    try:
        wish_index = int(wish_index)
    except ValueError:
        await send_message(
            session=session,
            chat_id=chat_id,
            text=f'please, enter valid index',
        )
        return

    wishes = await get_wishes_by_username(username)
    if len(wishes) <= wish_index:
        await send_message(
            session=session,
            chat_id=chat_id,
            text=f"you want delete wish thad doesn't exists",
        )
        return

    wish_for_deleting = wishes[wish_index]
    await delete_wish_by_id(wish_for_deleting[0])

    await send_message(
        session=session,
        chat_id=chat_id,
        text=f'successfully delete wish "{wish_for_deleting[1]}"',
    )


async def delete_private_user_command(
        chat_id: int,
        username: str,
        private_username: str,
        session: aiohttp.ClientSession):
    await delete_private_user(username, private_username)

    await send_message(
        session=session,
        chat_id=chat_id,
        text=f'private user "{private_username}" deleted successfully',
    )


async def message_handler(
        rb_message: RabbitMessage,
        session: aiohttp.ClientSession) -> None:
    if not rb_message.text.startswith('/'):
        return

    commands = rb_message.text[1:].split(' ')
    # remove elements = spaces. Need for case if user will
    # write commands with several spaces between commands
    commands = [command for command in commands if command]
    try:
        first_argument = commands[1]
    except IndexError:
        first_argument = None
    command_name = commands[0].lower()

    if command_name == 'add':
        await add_command(
            chat_id=rb_message.chat_id,
            username=rb_message.username,
            wish=' '.join(commands[1:]),
            session=session,
        )
    elif command_name == 'addpw':
        # shortening for add private wish
        await add_command(
            chat_id=rb_message.chat_id,
            username=rb_message.username,
            wish=' '.join(commands[1:]),
            session=session,
            private=True
        )
    elif command_name == 'addpu':
        # shortening for add private user
        await add_private_user_command(
            chat_id=rb_message.chat_id,
            username=rb_message.username,
            private_username=first_argument,
            session=session,
        )
    elif command_name == 'show':
        await show_command(
            chat_id=rb_message.chat_id,
            sender_of_command=rb_message.username,
            owner_of_wishes=first_argument,
            session=session,
        )
    elif command_name == 'showpu':
        await show_private_users_command(
            chat_id=rb_message.chat_id,
            username=rb_message.username,
            session=session,
        )
    elif command_name == 'delete':
        await delete_command(
            chat_id=rb_message.chat_id,
            username=rb_message.username,
            wish_index=first_argument,
            session=session,
        )
    elif command_name == 'deletepu':
        await delete_private_user_command(
            chat_id=rb_message.chat_id,
            username=rb_message.username,
            private_username=first_argument,
            session=session,
        )
    else:
        await send_message(
            session=session,
            chat_id=rb_message.chat_id,
            text=f"command doesn't exist",
        )


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
                    await message_handler(rb_message, session)
                    # TODO check if there needs of acknowledge

    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main())
