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
session = Session(bind=engine)

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher(bot=bot)


@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    users = session.query(User).all()

async def change(msg: types.Message):
    while True:
        if file_changed('req.py'):
            users = session.query(User).all()
            await send_message_to_users(text="File has been modified", users_list=[user.user_id for user in users])
@dp.message_handler(commands=["send_image"])
async def image_handler(msg: types.Message):
    await msg.answer_photo(photo="https://sun3-12.userapi.com/impg/CWmP0CXZl3wXrdY-yQVO_jx5S9ELLwtWI8_UXA/dtu77dXeMn8.jpg?size=604x604&quality=95&sign=413651e718d39434037e490854886050&c_uniq_tag=F1F0aNUjzENaBVmO4qrm3rsV98ZlOrtPSSusnphbJK4&type=album")
@dp.message_handler(commands=["send_audio"])
async def audio_handler(msg: types.Message):
   await bot.send_audio(audio="https://cs3-16v4.vkuseraudio.net/s/v1/acmp/diMdC2xNxxqCLQsR_HN16atTzM-EPFVx5lhv3ymPUf1UAjbWr9Ig0AakVkX10dxOlw3HcCF31vyG_JkgtMbtv2jEuNnQAdG4XBQMnUVieuD2JYUZ1l9H7dbF7otIgCxPnQFH6aP3kiBMsXDh76pB5TUZQzmqUKg3rq9Pv-nL_8r3vjMDcA.mp3", chat_id=msg.chat.id)
if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)