# aiogram imports
from aiogram import Bot, types, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from bot_keyboard import keyboard

# sqlalchemy imports
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy import update

# credentials imports
from db import url_object_async, User
from config import BOT_TOKEN

# other imports
import logging
import sys 
import asyncio


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot)

engine = create_async_engine(url=url_object_async)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

@dp.message(CommandStart())
async def start_handler(msg: types.Message):
    await msg.answer("""Добро пожаловать! Чтобы проверить, есть ли у вас подписка, нажмите кнопку /check.
                     
Если у вас есть подписка, можете нажать /updates_on, чтобы включить обновления. 
                     
Для их выключения нажмите /updates_off.""", reply_markup=keyboard)

async def check_user(user_id):
    async with async_session() as session:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        return user.updates

@dp.message(Command(commands=["check"]))
async def check_handler(msg: types.Message):
    if await check_user(msg.from_user.id):
        await msg.answer("У вас есть подписка!", reply_markup=keyboard)
    else:
        await msg.answer("У вас нет подписки!", reply_markup=keyboard)

async def switch_want_mode(msg: types.Message, mode):
    phrase_1 = "подключили" if mode else "отключили"
    phrase_2 = "подключены" if mode else "отключены"
    if await check_user(msg.from_user.id):
        async with async_session() as session:
            sel = select(User).where(User.user_id == msg.from_user.id)
            result = await session.execute(sel)
            user = result.scalars().first()
            if user.want_updates != mode:
                await session.execute(update(User).values(want_updates=mode).where(User.user_id == msg.from_user.id))
                await session.commit()
                await msg.answer(f"Вы {phrase_1} обновления")
            else:
                await msg.answer(f"У вас и так {phrase_2} обновления")
    else:
        await msg.answer("У вас нет доступа к функционалу бота. Попросите админа оформить подписку", reply_markup=keyboard)

@dp.message(Command(commands=["updates_off"]))
async def updates_off_handler(msg: types.Message):
    await switch_want_mode(msg, False)

@dp.message(Command(commands=["updates_on"]))
async def updates_on_handler(msg: types.Message):
    await switch_want_mode(msg, True)


async def main():
    tasks = [dp.start_polling(bot)]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())