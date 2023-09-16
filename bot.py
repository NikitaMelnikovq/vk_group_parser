from aiogram import Bot, types, Dispatcher
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import BOT_TOKEN
from sqlalchemy.future import select
import asyncio
from db import url_object_async, User
import logging
from aiogram import exceptions
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
import schedule
import time 
from aiogram.filters import Command, CommandStart
import sys 

async def send_message_to_users_handler(
    user_id: int, text: str, disable_notification: bool = False
) -> bool:
    """
    Safe messages sender
    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    try:
        await bot.send_message(
            user_id,
            text,
            disable_notification=disable_notification
        )
    except exceptions.BotBlocked:
        logging.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        logging.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        logging.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. "
            f"Sleep {e.timeout} seconds."
        )
        await asyncio.sleep(e.timeout)
        return await bot.send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        logging.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def send_message_to_users(text, users_list) -> int:
    """
    Simple broadcaster
    :return: Count of messages
    """
    count = 0
    try:
        for user_id in users_list:
            if await send_message_to_users_handler(user_id, text):
                count += 1
            # 20 messages per second (Limit: 30 messages per second)
            await asyncio.sleep(.05)
    finally:
        logging.info(f"{count} messages successful sent.")

    return count


bot = Bot(token=BOT_TOKEN)

dp = Dispatcher(bot=bot)

async def send_messages_to_users_handler():
    engine = create_async_engine(url=url_object_async)
    session = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session() as session:
        pass

async def send_messages_to_users():
    pass 

async def main():
    schedule.every(5).minutes.do()
    while True:
        schedule.run_pending()
        time.sleep(1)

@dp.message(CommandStart())
async def start_handler(msg: types.Message):
    ReplyKeyboardMarkup()
    settings_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton(text="/check")
    b2 = KeyboardButton(text="/updates_on")
    b3 = KeyboardButton(text="/updates_off")
    settings_keyboard.add(b1)
    settings_keyboard.add(b2)
    settings_keyboard.add(b3)
    await msg.answer("Добро пожаловать!\nЧтобы проверить, есть ли у вас подписка, нажмите кнопку /check\n\nЕсли у вас есть подписка, можете нажать /updates_on, чтобы включить обновления. Для их выключения нажмите /updates_off", reply_markup=settings_keyboard)

async def check_user(user_id):
    engine = create_async_engine(url=url_object_async)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with async_session() as session:
        stmt = select(User)
        result = await session.execute(stmt)
        users = result.scalars().all()
        users_id = [user.user_id for user in users if user.updates == 1]
        return user_id in users_id

@dp.message(Command(commands=["check"]))
async def check_handler(msg: types.Message):
    if await check_user(msg.from_user.id):
        await msg.answer("У вас есть подписка!")
    else:
        await msg.answer("У вас нет подписки!")

@dp.message(Command(commands=["updates_on"]))
async def updates_on_handler(msg: types.Message):
    if await check_user(msg.from_user.id):
        await msg.answer("Вы подключили обновления")
    else:
        await msg.answer("У вас нет доступа к функционалу бота. Попросите админа оформить подписку")

@dp.message(Command(commands=["updates_off"]))
async def updates_on_handler(msg: types.Message):
    if await check_user(msg.from_user.id):
        await msg.answer("Функционал допиливается")
    else:
        await msg.answer("У вас нет доступа к функционалу бота. Попросите админа оформить подписку")
async def main():
    await dp.start_polling(bot)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())