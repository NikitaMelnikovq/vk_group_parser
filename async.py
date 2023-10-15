from db import url_object_async, User
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
import asyncio

async def test(user_id):
    engine = create_async_engine(url=url_object_async)
    session = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session() as s:
        user = select(User).where(User.user_id == user_id)
        result = await s.execute(user)
        return result.scalars().all()

if __name__ == "__main__":
    asyncio.run(test(863190796))
    asyncio.get_event_loop().close()
