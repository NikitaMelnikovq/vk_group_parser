from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import asyncio 
from db import url_object, User
import logging, sys  

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

async def send_messages():
    engine = create_engine(url=url_object) 
    session = Session(bind=engine)
    user = session.query(User).first()
    
    await bot.send_message(chat_id=user.user_id, text="")

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    tasks = [dp.start_polling(bot), send_messages()]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
