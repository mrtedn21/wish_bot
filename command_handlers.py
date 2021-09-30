from sqlalchemy import text

from db import engine


def add_command_handler(update, context):
    args = context.args
    user = update.message.from_user
    first_name = user['first_name']

    if len(args):
        wish_value = ' '.join(args)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='write wish')
        return

    with engine.connect() as conn:
        insert_wish_query = text("INSERT INTO wish(first_name, text) values(:first_name, :text)")
        conn.execute(insert_wish_query, first_name=first_name, text=wish_value)

    context.bot.send_message(chat_id=update.effective_chat.id, text='ok')


def show_command_handler(update, context):
    args = context.args

    if not len(args):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='write first_name, whose wishes you want to watch'
        )
        return

    first_name_for_showing = args[0]

    resulting_message = ''

    with engine.connect() as conn:
        select_query = text("SELECT * FROM wish WHERE first_name = :first_name")
        result = conn.execute(select_query, first_name=first_name_for_showing)

        for wish in result:
            resulting_message = f'{resulting_message}\n{wish[1]}'

    context.bot.send_message(chat_id=update.effective_chat.id, text=resulting_message)
