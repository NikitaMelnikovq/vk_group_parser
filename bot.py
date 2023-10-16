# aiogram imports
from aiogram import Bot, types, Dispatcher
from aiogram.filters import Command, CommandStart
from bot_keyboard import keyboard
from aiogram.exceptions import TelegramAPIError

# sqlalchemy imports
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy import update

# credentials imports
from db import url_object_async, User, Last_message, Post
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
    await msg.answer("""Привет! Нажми /info, чтобы получить подробную информацию""", reply_markup=keyboard)

@dp.message(Command("info"))
async def info_handler(msg: types.Message):
    await msg.answer(text="""Добро пожаловать! Чтобы проверить, есть ли у вас подписка, нажмите кнопку /check.
                     
Если у вас есть подписка, можете нажать /updates_on, чтобы включить обновления. 
                     
Для их выключения нажмите /updates_off.
                     
Хочу обратить внимание, что чтобы посмотреть детальную информацию о посте (картинки, аудио, видео), нужно перейти по ссылке.
Пока что в боте такой возможности нет.
                     
Внимание! Бот работает в тестовом режиме, некоторые функции могут быть недоступны.""", reply_markup=keyboard)
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
                await msg.answer(f"Вы {phrase_1} обновления", reply_markup=keyboard)
            else:
                await msg.answer(f"У вас и так {phrase_2} обновления", reply_markup=keyboard)
    else:
        await msg.answer("У вас нет доступа к функционалу бота. Попросите админа оформить подписку", reply_markup=keyboard)

@dp.message(Command(commands=["updates_off"]))
async def updates_off_handler(msg: types.Message):
    await switch_want_mode(msg, False)

@dp.message(Command(commands=["updates_on"]))
async def updates_on_handler(msg: types.Message):
    await switch_want_mode(msg, True)

async def send_messages(user):
    async with async_session() as session:
        select_last_message = select(Last_message)
        result = await session.execute(select_last_message) 
        date = result.scalars().first()
        select_posts = select(Post).where(Post.identity_date > date.id_date).order_by(Post.identity_date.asc())
        posts = await session.execute(select_posts)
        posts = posts.scalars().all()
        for post in posts:
            final_message = ""
            final_message += str(post.group_name) + "\n\n"
            final_message += str(post.post_date) + "\n\n"
            final_message += str(post.post_text) + "\n\n"
            final_message += "Ссылка на пост: " + str(post.post_link) + "\n"
            await bot.send_message(chat_id=user.user_id, text=final_message)
            await asyncio.sleep(1)
            await session.execute(update(Last_message).values(id_date=post.identity_date))
            await session.commit()

async def send_message_to_users():
    while True:
        async with async_session() as session:
            select_users = select(User).where(User.updates == 1)
            result = await session.execute(select_users)
            users = result.scalars().all()
            for user in users:
                try:
                    await send_messages(user)
                except TelegramAPIError as e:
                    print("Bot blocked")
async def main():
    tasks = [dp.start_polling(bot), send_message_to_users()]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())