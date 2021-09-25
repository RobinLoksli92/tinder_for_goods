from textwrap import dedent

from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler
from telegram.ext import Filters
from telegram import InlineKeyboardMarkup

import keyboards
from helpers import go_back


states_database = {}
goods_database = {}
current_good_database = {}


def start(update: Update, context: CallbackContext):
    chat_id = update.effective_message.chat_id

    context.bot.send_message(
        chat_id=chat_id,
        text='Выбери действие',
        reply_markup=InlineKeyboardMarkup(keyboards.keyboard)
    )

    return 'MAIN_MENU'


def main_menu_handler(update: Update, context: CallbackContext):
    data = update.callback_query.data
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id
    
    if data == 'add':
        context.bot.send_message(
            chat_id=chat_id,
            text='Заполни анкету вещи:',
            reply_markup=InlineKeyboardMarkup(keyboards.keyboard_add)
        )
        context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
        return 'ADD_GOOD'
    elif data == 'find':
        goods = goods_database.get(chat_id)
        good = goods[0]

        context.bot.send_photo(
            chat_id=chat_id,
            caption=f'Title: {good.get("title", "")}\nSome description',
            photo=good.get('photo'),
            reply_markup=InlineKeyboardMarkup(keyboards.keyboard_find)
        )
        context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
        return 'FIND_GOOD'
    elif data == 'goods':
        goods = goods_database.get(chat_id, {})
        text = ''
        for good in goods:
            text += f"""\
            Title: {good['title']}
            Photo: {good['photo']}


            """
        context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )

        context.bot.send_message(
            chat_id=chat_id,
            text=dedent(text),
            reply_markup=InlineKeyboardMarkup(keyboards.keyboard),
            disable_web_page_preview=True
        )

        return 'MAIN_MENU'

    return 'MAIN_MENU'


def goods_handler(update: Update, context: CallbackContext):
    return 'GOODS'


def add_good_handler(update: Update, context: CallbackContext):
    data = update.callback_query.data
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id

    if data == 'add_title':
        prev_message_id = context.bot.send_message(
            chat_id=chat_id,
            text='Введи название товара: '
        ).message_id
        context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
        context.chat_data['previous_message'] = prev_message_id
        return 'ADD_GOOD_TITLE'
    elif data == 'add_photo':
        prev_message_id = context.bot.send_message(
            chat_id=chat_id,
            text='Дай ссылку на картинку: '
        ).message_id
        context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
        context.chat_data['previous_message'] = prev_message_id
        return 'ADD_GOOD_PHOTO'
    elif data == 'done':
        good = current_good_database.get(chat_id, {})
        text = ''
        if not good:
            text += 'Невалидный товар\n'
        if not good.get('title'):
            text += 'Отсутствует название\n'
        if not good.get('photo'):
            text += 'Отсутствует картинка'
        if good:
            text = 'Товар успешно добавлен'
            user_goods = goods_database.get(chat_id, [])
            user_goods.append(good)
            goods_database.update({chat_id: user_goods})
            current_good_database[chat_id] = {}

        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboards.keyboard)
        )
        context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
        return 'MAIN_MENU'
    elif data == 'back':
        go_back(context, chat_id, message_id)
        return 'MAIN_MENU'


def add_good_title_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id
    user_input = update.message.text

    current_good = current_good_database.get(chat_id, {})
    current_good['title'] = user_input
    current_good_database.update({chat_id: current_good})

    if photo := current_good.get('photo'):
        context.bot.send_photo(
            chat_id=chat_id,
            caption=f'Title: {user_input}\nSome description',
            photo=photo,
            reply_markup=InlineKeyboardMarkup(keyboards.keyboard_add)
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Title: {user_input}\nSome description',
            reply_markup=InlineKeyboardMarkup(keyboards.keyboard_add)
        )
    if prev_message_id := context.chat_data.get('previous_message'):
        context.bot.delete_message(
            chat_id=chat_id,
            message_id=prev_message_id
        )

    context.bot.delete_message(
        chat_id=chat_id,
        message_id=message_id
    )

    return 'ADD_GOOD'


def add_good_photo(update: Update, context: CallbackContext):
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id
    user_input = update.message.text

    current_good = current_good_database.get(chat_id, {})
    current_good['photo'] = user_input

    context.bot.send_photo(
        chat_id=chat_id,
        caption=f'Title: {current_good.get("title", "")}\nSome description',
        photo=user_input,
        reply_markup=InlineKeyboardMarkup(keyboards.keyboard_add)
    )

    if prev_message_id := context.chat_data.get('previous_message'):
        context.bot.delete_message(
            chat_id=chat_id,
            message_id=prev_message_id
        )

    context.bot.delete_message(
        chat_id=chat_id,
        message_id=message_id
    )

    return 'ADD_GOOD'


def find_good_handler(update: Update, context: CallbackContext):
    data = update.callback_query.data
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id

    if data == 'back':
        go_back(context, chat_id, message_id)
        return 'MAIN_MENU'


def handle_users_reply(update: Update, context: CallbackContext):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data  # text
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = states_database.get(chat_id)  # {chat_id = state}  # есть только стейт

    states_functions = {
        'START': start,
        'MAIN_MENU': main_menu_handler,
        'GOODS': goods_handler,

        'ADD_GOOD': add_good_handler,
        'ADD_GOOD_TITLE': add_good_title_handler,
        'ADD_GOOD_PHOTO': add_good_photo,

        'FIND_GOOD': find_good_handler,
    }

    state_handler = states_functions[user_state]  # state_hander = states_functions['START']  # определяем какую функцию нужно дернуть на этом стейте
    # state_handler - callback-функция
    next_state = state_handler(update, context)  # MAIN_MENU
    states_database.update({chat_id: next_state})  # {chat_id = MAIN_MENU}


def main():
    token = '1484358818:AAF8671_E1IVK1CUG_DwqgmnaONAsIAHotE'
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    updater.start_polling()


if __name__ == '__main__':
    main()
