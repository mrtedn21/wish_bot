import os

from telegram.ext import Updater, CommandHandler
from sqlalchemy import text
from dotenv import load_dotenv

from db import engine

load_dotenv()


def add(update, context):
    args = context.args
    user = update.message.from_user
    username = user['username']

    if len(args):
        wish_value = ' '.join(args)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='write wish')
        return

    with engine.connect() as conn:
        insert_wish_query = text("INSERT INTO wish(username, text) values(:username, :text)")
        conn.execute(insert_wish_query, username=username, text=wish_value)

    context.bot.send_message(chat_id=update.effective_chat.id, text='ok')


def show(update, context):
    args = context.args

    if not len(args):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='write username, whose wishes you want to watch'
        )
        return

    username_for_showing = args[0]

    resulting_message = ''

    with engine.connect() as conn:
        select_query = text("SELECT * FROM wish WHERE username = :username")
        result = conn.execute(select_query, username=username_for_showing)
        for wish in result:
            resulting_message = f'{resulting_message}\n{wish[1]}'

    context.bot.send_message(chat_id=update.effective_chat.id, text=resulting_message)


telegram_bot_token = os.getenv('WISH_APP_TOKEN')

updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher

add_handler = CommandHandler('add', add)
dispatcher.add_handler(add_handler)

show_handler = CommandHandler('show', show)
dispatcher.add_handler(show_handler)

updater.start_polling()
