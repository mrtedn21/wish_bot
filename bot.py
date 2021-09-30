import os

from telegram.ext import Updater, CommandHandler
from dotenv import load_dotenv

from command_handlers import add_command_handler, show_command_handler

load_dotenv()

telegram_bot_token = os.getenv('WISH_APP_TOKEN')

updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher

add_handler = CommandHandler('add', add_command_handler)
dispatcher.add_handler(add_handler)

show_handler = CommandHandler('show', show_command_handler)
dispatcher.add_handler(show_handler)

updater.start_polling()
