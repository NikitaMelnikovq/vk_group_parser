from config import BOT_TOKEN
from aiogram import Bot, Dispatcher, types 
from aiogram.filters import CommandStart
import asyncio

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot)

@dp.message(CommandStart())
async def main(msg: types.Message):
    await msg.answer("h")
    print(msg.chat.id)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())