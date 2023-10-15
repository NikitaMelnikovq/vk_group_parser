from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

kb = [
    [KeyboardButton(text="/check")],
    [KeyboardButton(text="/updates_on")],
    [KeyboardButton(text="/updates_off")],
    [KeyboardButton(text="/info")],
]
keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)