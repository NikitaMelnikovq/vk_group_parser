from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import asyncio 
from db import url_object, User, Post
import logging
from bot_events import router

bot = Bot(token=BOT_TOKEN)

async def send_message(bot: Bot, user, post: Post):
    group_name = post.group_name
    post_link = post.post_link
    post_text = post.post_text
    post_date = post.post_date 

    post_message = f"{group_name}\n{post_date}\n\n{post_text}\n{post_link}"
    await bot.send_message(chat_id=user.user_id, text=post_message)

async def send_messages():
    engine = create_engine(url=url_object, pool_recycle=3600) 

    while True:
        # Use the with statement to manage the session
        with Session(bind=engine, expire_on_commit=False) as session:
            user = session.query(User).filter(User.updates == 1 and User.want_updates == 1).first()
            posts = session.query(Post).filter(Post.sent == 0).all()

            for post in posts:
                await send_message(bot, user, post)
                session.query(Post).filter(Post.post_id == post.post_id).update({"sent": 1})

            session.commit()
        await asyncio.sleep(5)

async def main():
    logging.basicConfig(level=logging.INFO)

    dp = Dispatcher()
    dp.include_router(router)

    tasks = [dp.start_polling(bot), send_messages()]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
