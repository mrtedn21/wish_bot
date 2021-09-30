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
        select_query = text("SELECT * FROM wish WHERE LOWER(first_name) = LOWER(:first_name) ORDER BY text")
        result = conn.execute(select_query, first_name=first_name_for_showing)

        index = 0
        for wish in result:
            index += 1
            resulting_message = f'{resulting_message}\n{index}. {wish[1]}'

        if not resulting_message:
            context.bot.send_message(chat_id=update.effective_chat.id, text='not found wishes for this user')
            return

    context.bot.send_message(chat_id=update.effective_chat.id, text=resulting_message)


def delete_command_handler(update, context):
    args = context.args
    if len(args) < 2:
        context.bot.send_message(chat_id=update.effective_chat.id, text='not all parameters were passed')
        return

    first_name = args[0]
    try:
        wish_index_for_deleting = int(args[1])
    except ValueError:
        context.bot.send_message(chat_id=update.effective_chat.id, text='invalid index')
        return

    with engine.connect() as conn:
        delete_query = text("""
            DELETE FROM wish
            WHERE EXISTS (
                SELECT 1 FROM (
                    SELECT
                        first_name,
                        text,
                        ROW_NUMBER() OVER(PARTITION BY first_name ORDER BY text) AS rn
                    FROM wish
                    WHERE LOWER(first_name) = LOWER(:first_name)
                ) child
                WHERE rn = :index
                  AND child.first_name = wish.first_name
                  AND child.text = wish.text
            )
        """)

        conn.execute(delete_query, first_name=first_name, index=wish_index_for_deleting)

    context.bot.send_message(chat_id=update.effective_chat.id, text='ok')
