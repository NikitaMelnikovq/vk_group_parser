from aiogram import Bot, executor, types, Dispatcher
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import Session
from config import BOT_TOKEN
import asyncio
from observer import file_changed
from db import url_object, User
import logging
from aiogram import exceptions
from sqlalchemy.exc import IntegrityError


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

engine = create_engine(url=url_object, pool_recycle=3600, echo=True)

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher(bot=bot)

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    session = Session(bind=engine)


    table = Table("Users", MetaData(), autoload_with=engine)
    try:
        record = table.insert().values(user_id=msg.from_user.id, chat_id=msg.chat.id)
        session.execute(statement=record)
        await msg.answer(text="You subscribed to my bot", parse_mode="HTML")
        session.commit()
        session.close()
    except IntegrityError:
        await msg.answer(text="You already subscirbed to my bot")
    while True:
        if file_changed('data.json'):
            users = session.query(User).all()
            await send_message_to_users(text="File has been modified", users_list=[user.user_id for user in users])

if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)