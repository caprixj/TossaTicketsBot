import asyncio
import logging
import os
import sys
from pathlib import Path

import aiosqlite
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

import config_handler
from middleware.SourceFilterMiddleware import SourceFilterMiddleware
from model.Member import Member
from model.RunMode import RunMode
from utilities.constant import CREATOR_USER_ID, WRONG_COMMAND_ARGUMENTS_TEXT, TICKETS_ADDED_TEXT, NO_REPLY_TEXT, \
    MEMBER_TICKETS_COUNT_TEXT, NO_NAMES_TEXT
from repository.MemberRepository import MemberRepository
from service.MemberService import MemberService
from utilities.utils import get_random_permission_denied_message, get_command_args

config_file_dev = str(Path('config') / 'config.xml')
config_file_deploy = str(Path.cwd().parent / Path('config') / 'config.xml')

TOKEN = config_handler.getvar('BOT_TOKEN', config_file_deploy, config_file_dev)

members_db_prod = str(Path.cwd().parent / Path('db') / 'members.db')
members_db_dev = str(Path('db') / 'members.db')
members_db_path = ''

dp = Dispatcher()
dp.message.middleware(SourceFilterMiddleware())

run_mode = RunMode.DEFAULT
service = MemberService(MemberRepository())


@dp.message(Command("reg"))
async def test_initial_reg(message: Message) -> None:
    if await service.member_exists(message.from_user.id):
        await message.answer("уже регався. іди нахуй")
    else:
        new_member = Member(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        await service.create(new_member)
        await message.answer("+")


@dp.message(Command("balance"))
async def get_balance(message: Message) -> None:
    tickets_count = await service.get_balance(message)
    member_info = ''

    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    if first_name or last_name:
        fn_not_empty = False
        if first_name:
            fn_not_empty = True
            member_info += first_name
        if last_name:
            member_info += ' ' if fn_not_empty else ''
            member_info += last_name
    elif username:
        member_info += '@' + username
    else:
        member_info = NO_NAMES_TEXT

    member_info = f"[{member_info}](tg://user?id={user_id})"

    await message.reply(f'{member_info}\n{MEMBER_TICKETS_COUNT_TEXT}: {tickets_count}')


#  /add_tickets <count>
@dp.message(Command("add_tickets"))
async def add_tickets(message: Message) -> None:
    if message.from_user.id != CREATOR_USER_ID:
        await message.reply(await get_random_permission_denied_message())
        return

    if message.reply_to_message is None:
        await message.reply(NO_REPLY_TEXT)
        return

    args = await get_command_args(message.text)

    if len(args) == 0:
        await message.reply(WRONG_COMMAND_ARGUMENTS_TEXT)
        return

    arg = args[0]

    if not arg.isdigit():
        await message.reply(WRONG_COMMAND_ARGUMENTS_TEXT)
        return

    print(int(arg))
    if int(arg) == 0:
        await message.reply(WRONG_COMMAND_ARGUMENTS_TEXT)
        return

    await service.add_tickets(message, int(arg))
    await message.reply(TICKETS_ADDED_TEXT)


@dp.message(Command("remove_tickets"))
async def remove_tickets(message: Message) -> None:
    pass


@dp.message(Command("set_tickets"))
async def set_tickets(message: Message) -> None:
    pass


async def create_databases():
    # members.db
    os.makedirs(os.path.dirname(members_db_path), exist_ok=True)

    async with aiosqlite.connect(members_db_path) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS members (
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            tickets_count INTEGER DEFAULT 0,
            unique_artifacts TEXT
        );
        """)
        await db.commit()


def define_run_mode() -> RunMode:
    if len(sys.argv) <= 1:
        return RunMode.DEFAULT

    if sys.argv[1] == "dev":
        return RunMode.DEV
    elif sys.argv[1] == "prod":
        return RunMode.PROD


def define_db_path() -> bool:
    global members_db_path

    if run_mode == RunMode.PROD:
        members_db_path = members_db_prod
        service.repo.db_path = members_db_path
        return True
    elif run_mode == RunMode.DEV:
        members_db_path = members_db_dev
        service.repo.db_path = members_db_path
        return True
    else:
        return False


async def main() -> None:
    await create_databases()

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    await dp.start_polling(bot)


if __name__ == "__main__":
    run_mode = define_run_mode()
    valid_args = define_db_path()

    if not valid_args:
        raise RuntimeError("THE PROGRAM WAS STARTED WITH INVALID COMMAND PARAMETERS!")

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
