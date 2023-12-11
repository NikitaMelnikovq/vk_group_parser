from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from db import url_object

router = Router()

async def create_session() -> Session:
    engine = create_engine(url=url_object)
    session = Session(bind=engine)

    return session

@router.message(CommandStart())
async def start_command(msg: Message):
    pass