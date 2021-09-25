from telegram import InlineKeyboardButton

keyboard = [
    [InlineKeyboardButton('Добавить вещь', callback_data='add')],
    [InlineKeyboardButton('Посмотреть свои вещи', callback_data='goods')],  # TODO реализовать возможность смотреть свои вещи
    [InlineKeyboardButton('Найти вещь', callback_data='find')],
]

keyboard_add = [
    [InlineKeyboardButton('Ввести название', callback_data='add_title')],
    [InlineKeyboardButton('Отправить фото вещи', callback_data='add_photo')],
    [InlineKeyboardButton('Готово', callback_data='done')],
    [InlineKeyboardButton('Назад', callback_data='back')],
]

keyboard_find = [
    [
        InlineKeyboardButton('Не нравится', callback_data='not'),
        InlineKeyboardButton('Нравится', callback_data='like')
    ],
    [InlineKeyboardButton('Назад', callback_data='back')],
]