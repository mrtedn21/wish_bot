import os

from telegram.ext import Updater, CommandHandler
from dotenv import load_dotenv

load_dotenv()


def add(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='ok')


telegram_bot_token = os.getenv('WISH_APP_TOKEN')

updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('add', add)
dispatcher.add_handler(start_handler)

updater.start_polling()
