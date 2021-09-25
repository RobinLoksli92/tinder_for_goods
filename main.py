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
        text='Привет! Я помогу тебе обменять что-то ненужное на очень нужное. Чтобы разместить вещь к обмену напиши - “Добавить вещь”. После этого тебе станут доступны вещи других пользователей. Напиши “Найти вещь” и я пришлю тебе фотографии вещей для обмена. Понравилась вещь - пиши “Обменяться”, нет - снова набирай “Найти вещь”. Нажал “обменяться”? - если владельцу вещи понравится что-то из твоих вещей, то я пришлю контакты вам обоим.',
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
            text='Введи название вещи и отправь ссылку на её фото :',
            reply_markup=InlineKeyboardMarkup(keyboards.keyboard_add)
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
        return 'FIND_GOOD'

    return 'MAIN_MENU'



def add_good_handler(update: Update, context: CallbackContext):
    data = update.callback_query.data
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id

    if data == 'add_title':
        context.bot.send_message(
            chat_id=chat_id,
            text='Введите название вашей вещи: '
        )
        return 'ADD_GOOD_TITLE'
    elif data == 'add_photo':
        context.bot.send_message(
            chat_id=chat_id,
            text='Дай ссылку на картинку: '
        )
        return 'ADD_GOOD_PHOTO'
    elif data == 'done':
        good = current_good_database.get(chat_id, {})
        text = ''
        if not good:
            text += 'Нет вещи\n'
        if not good.get('title'):
            text += 'Отсутствует название\n'
        if not good.get('photo'):
            text += 'Отсутствует картинка'
        if good:
            text = 'Вещь успешно добавлена'
            user_goods = goods_database.get(chat_id, [])
            user_goods.append(good)
            goods_database.update({chat_id: user_goods})
            current_good_database[chat_id] = {}

        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboards.keyboard)
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
    token = '2022928188:AAEPoWTruKXN6nRZr6ranRUPzIr8Bum__XM'
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    updater.start_polling()


if __name__ == '__main__':
    main()
