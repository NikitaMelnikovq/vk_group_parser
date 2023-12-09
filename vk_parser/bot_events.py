from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session
from db import url_object, User, Group
from bot_keyboard import keyboard
from functions import convert_time, get_group_id, add_group_name
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import time 
from sqlalchemy.exc import IntegrityError

class StateMachine(StatesGroup):
    await_link = State()
    await_remove = State()

router = Router()

def close_session(session: Session) -> None:
    session.commit()
    session.close()

def create_session() -> Session:
    engine = create_engine(url=url_object)
    return Session(bind=engine)

async def send_message(msg: Message, text: str) -> None:
    await msg.answer(text=text, reply_markup=keyboard)

async def check_user(user_id) -> bool:
    session = create_session()
    user = session.query(User).filter(User.user_id == user_id, User.want_updates == 1).first()
    session.close()
    return user is not None

async def start(msg: Message) -> None:
    session = create_session()
    user = session.query(User).filter(User.user_id == msg.from_user.id).first()

    if user:
        await send_message(msg, "Добро пожаловать обратно")
    else:
        await send_message(msg, "Добро пожаловать!")

        new_user = User(
            join_time=convert_time(time.time()),
            updates=0,
            want_updates=0,
            user_id=msg.from_user.id
        )

        session.add(new_user)

    close_session(session=session)

@router.message(CommandStart(ignore_case=True))
async def start_command_handler(msg: Message):
    await start(msg)

@router.message(Command("add_group", ignore_case=True))
async def add_group_command_handler(msg: Message, state: FSMContext):
    if await check_user(msg.from_user.id):
        await send_message(msg, "Введите ссылку на группу: ")
        await state.set_state(StateMachine.await_link)
    else:
        await send_message(msg, "У вас нет разрешения использовать эту функцию бота!")

@router.message(StateMachine.await_link, F.text != "/stop")
async def accept_link(msg: Message, state: FSMContext):
    session = create_session()
    groups = session.query(Group).all()

    if len(groups) > 20:
        await send_message(msg, "Не рекомендовано добавление больше 20 групп. Придётся увеличить интервал и исправлять код")
        await state.clear()
    else:
        try:
            group_id = get_group_id(msg.text)
            group_name = add_group_name(group_id)
            new_group = Group(group_id=group_id, group_name=group_name)
            session.add(new_group)
            close_session(session=session)

        except IntegrityError as ie:
            await send_message(msg,"You've already added this group")

        finally:
            time.sleep(0.4)
            await send_message(msg, "Отправьте ещё одну группу или нажмите /stop")
@router.message(Command("remove_group", ignore_case=True))
async def remove_group_command_handler(msg: Message, state: FSMContext):
    if await check_user(msg.from_user.id):
        await send_message(msg, "Введите ссылку на группу: ")
        await state.set_state(StateMachine.await_remove)
    else:
        await send_message(msg, "У вас нет разрешения использовать эту функцию бота!")

@router.message(F.text != "/stop", StateMachine.await_remove)
async def remove_link(msg: Message):
    session = create_session()
    group_id = get_group_id(msg.text)
    delete_group = delete(Group).filter(Group.group_id == group_id)
    session.execute(delete_group)

    await send_message(msg, "Введите следующую группу или нажмите /stop")
    close_session(session=session)

@router.message(Command("stop"), StateMachine.await_link)
@router.message(Command("stop"), StateMachine.await_remove)
async def stop_accepting(msg: Message, state: FSMContext):
    await state.clear()
    await send_message(msg, "Вы отменили ввод")

@router.message(Command("get_id", ignore_case=True))
async def print_id(msg: Message):
    await msg.answer(text=f"Ваш ID: <b>{msg.from_user.id}</b>", parse_mode="HTML", reply_markup=keyboard)

@router.message(Command("updates_on", ignore_case=True))
async def turn_on_updates(msg: Message):
    session = create_session()
    user = session.query(User).filter(User.user_id == msg.from_user.id)
    if user.first().want_updates == 1:
        await msg.answer(text="У вас уже подключены обновления")
    else:
        await msg.answer(text="Вы подключили обновления")
        session.query(User).filter(User.user_id == msg.from_user.id).filter(User.want_updates == 1).update({"want_updates": 0})
        close_session(session=session)

@router.message(Command("updates_off", ignore_case=True))
async def turn_on_updates(msg: Message):
    session = create_session()
    user = session.query(User).filter(User.user_id == msg.from_user.id)
    if user.first().want_updates == 0:
        await msg.answer(text="У вас уже отключены обновления")
    else:
        await msg.answer(text="Вы отключили обновления")
        session.query(User).filter(User.user_id == msg.from_user.id).filter(User.want_updates == 0).update({"want_updates": 1})
        close_session(session=session)
        