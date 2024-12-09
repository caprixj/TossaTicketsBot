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
from model.Member import Member
from repository.MemberRepository import MemberRepository
from service.MemberService import MemberService

config_file_dev = str(Path('config') / 'config.xml')
config_file_deploy = str(Path.cwd().parent / Path('config') / 'config.xml')

TOKEN = config_handler.getvar('BOT_TOKEN', config_file_deploy, config_file_dev)

members_db_prod = str(Path.cwd().parent / Path('db') / 'members.db')
members_db_ide = str(Path('db') / 'members.db')
members_db_path = ''

dp = Dispatcher()
member_service = MemberService(MemberRepository(members_db_path))


@dp.message(Command("reg"))
async def test_initial_reg(message: Message) -> None:
    await member_service.reset_dp_path(members_db_path)

    if await member_service.user_exists(message.from_user.id):
        await message.answer("уже регався. іди нахуй")
    else:
        new_member = Member(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        await member_service.create(new_member)
        await message.answer("+")


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


def define_db_path():
    global members_db_path

    if len(sys.argv) > 1 and sys.argv[1] == "prod":
        members_db_path = members_db_prod
    else:
        members_db_path = members_db_ide


async def main() -> None:
    await create_databases()

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    define_db_path()

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
