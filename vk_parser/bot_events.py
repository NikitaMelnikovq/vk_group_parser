from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from config import BOT_TOKEN
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session
import asyncio 
from db import url_object, User, Group
from bot_keyboard import keyboard
import time
from functions import convert_time, get_group_id, create_error_log, add_group_name
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

class StateMachine(StatesGroup):
    await_link = State()
    await_remove = State()
router = Router()

async def check_user(user_id):
    engine = create_engine(url=url_object)
    session = Session(bind=engine)

    user = session.query(User).filter(User.user_id == user_id).filter(User.updates == 1).all()

    return len(user) != 0


@router.message(CommandStart(ignore_case=True))
async def start(msg: Message):
    engine = create_engine(url=url_object)
    session = Session(bind=engine)
    user = session.query(User).filter(User.user_id == msg.from_user.id).all()
    if user:
        await msg.answer(text="Добро пожаловать обратно", reply_markup=keyboard)
    else:
        await msg.answer(text="Добро пожаловать!", reply_markup=keyboard)
        new_user = User()
        new_user.join_time = convert_time(time.time())
        new_user.updates = 0
        new_user.want_updates = 0
        new_user.user_id = msg.from_user.id
        session.add(new_user)
    session.commit()
    session.close()

@router.message(Command("add_group", ignore_case=True))
async def add_group(msg: Message, state: FSMContext):
    if await check_user(msg.from_user.id):
        await msg.answer(text="Введите ссылку на группу: ")
        await state.set_state(StateMachine.await_link)
    else:
        await msg.answer(text="У вас нет разрешения использовать эту функцию бота!", reply_markup=keyboard)


@router.message(StateMachine.await_link, F.text)
async def accept_link(msg: Message, state: FSMContext):
    engine = create_engine(url=url_object)
    session = Session(bind=engine)
    groups = session.query(Group).all()
    if len(groups) > 20:
        await msg.answer(text="Не рекомендовано добавление больше 20 групп. Придётся увеличить интервал и исправлять код")
        await state.clear()
    else:
        try:
            group_id = get_group_id(msg.text)
            group_name = add_group_name(group_id)
            new_group = Group(group_id=group_id, group_name=group_name)
            session.add(new_group)
        except Exception as e:
            create_error_log(str(e))
    await msg.answer(text="Отправьте ещё одну группу или нажмите /stop")
    session.commit()
    session.close()

@router.message(Command("remove_group", ignore_case=True))
async def remove_group(msg: Message, state: FSMContext):
    if await check_user(msg.from_user.id):
        await msg.answer(text="Введите ссылку на группу: ")
        await state.set_state(StateMachine.await_remove)
    else:
        await msg.answer(text="У вас нет разрешения использовать эту функцию бота!", reply_markup=keyboard)

@router.message(F.text, StateMachine.await_remove)
async def remove_link(msg: Message):
    engine = create_engine(url=url_object)
    session = Session(bind=engine)
    group_id = get_group_id(msg.text)
    delete_group = delete(Group).filter(Group.group_id == group_id)
    session.execute(delete_group)
    await msg.answer("Введите следующую группу или нажмите /stop")
    session.commit()
    session.close()

@router.message(Command("stop"), StateMachine.await_link)
async def stop_accepting(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(text="Вы отменили ввод групп")

@router.message(Command("get_id", ignore_case=True))
async def print_id(msg: Message):
    await msg.answer(text=f"Ваш ID: <b>{msg.from_user.id}</b>", parse_mode="HTML", reply_markup=keyboard)