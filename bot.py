from aiogram import Dispatcher, Bot, types, executor
from config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN)

dp = Dispatcher(bot=bot)

@dp.message_handler(commands=["start"])
async def main_commands(msg: types.Message):
    pass


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)