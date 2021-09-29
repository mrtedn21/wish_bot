import os

from telegram.ext import Updater, CommandHandler
from sqlalchemy import text
from dotenv import load_dotenv

from db import engine

load_dotenv()


def add(update, context):
    args = context.args

    if len(args):
        wish_value = ' '.join(args)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='write wish')
        return

    with engine.connect() as conn:
        insert_wish_query = text("INSERT INTO wish(name) values(:name)")
        conn.execute(insert_wish_query, name=wish_value)

    context.bot.send_message(chat_id=update.effective_chat.id, text='ok')


telegram_bot_token = os.getenv('WISH_APP_TOKEN')

updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('add', add)
dispatcher.add_handler(start_handler)

updater.start_polling()
