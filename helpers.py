from telegram import InlineKeyboardMarkup

import keyboards


def go_back(context, chat_id, message_id):
    context.bot.send_message(
        chat_id=chat_id,
        text='Выбери действие',
        reply_markup=InlineKeyboardMarkup(keyboards.keyboard)
    )
