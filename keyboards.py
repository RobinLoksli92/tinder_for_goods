from telegram import InlineKeyboardButton

keyboard = [
    [InlineKeyboardButton('Добавить вещь', callback_data='add')],
    [InlineKeyboardButton('Обменяться', callback_data='exchange')],  # TODO реализовать возможность смотреть свои вещи
    [InlineKeyboardButton('Найти вещь', callback_data='find')],
]

keyboard_add = [
    [InlineKeyboardButton('Ввести название', callback_data='add_title')],
    [InlineKeyboardButton('Отправить фото вещи', callback_data='add_photo')],
    [InlineKeyboardButton('Готово', callback_data='done')],
]

keyboard_find = [
    [
        InlineKeyboardButton('Не нравится', callback_data='not'),
        InlineKeyboardButton('Нравится', callback_data='like')
    ],
]