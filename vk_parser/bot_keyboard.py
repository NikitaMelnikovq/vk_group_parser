from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

kb = [
    [KeyboardButton(text="/add_group")],
    [KeyboardButton(text="/updates_on"), KeyboardButton(text="/updates_off")],
    [KeyboardButton(text="/get_id"), KeyboardButton(text="/info")],
]
keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)