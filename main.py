import asyncio
import logging
import os
import sys

import aiosqlite
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from middleware.SourceFilterMiddleware import SourceFilterMiddleware
from model.functional.command_const import CommandPattern
from model.functional.command_const import CommandPattern as cp
from model.functional.RunMode import RunMode
from utilities.CommandParser import CommandParser
from utilities.global_vars import GlobalVariables as gv
from repository.MemberRepository import MemberRepository
from service.MemberService import MemberService
from utilities.utils import get_random_permission_denied_message, get_command_args, get_run_mode_settings

service = MemberService(MemberRepository())

dp = Dispatcher()


@dp.message(Command("balance"))
async def balance(message: Message) -> None:
    user = message.from_user \
        if message.reply_to_message is None \
        else message.reply_to_message.from_user

    tickets_count = await service.get_balance(user)
    member_info = ''

    user_id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name

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
        member_info = gv.NO_NAMES_TEXT

    member_info = f"[{member_info}](tg://user?id={user_id})"

    await message.reply(f'{member_info}\n{gv.MEMBER_TICKETS_COUNT_TEXT}: {tickets_count}')


@dp.message(Command(cp.addt.name))
async def addt(message: Message) -> None:
    if message.from_user.id != gv.CREATOR_USER_ID:
        await message.reply(await get_random_permission_denied_message())
        return

    command_parser = CommandParser(message, cp.addt.value)
    result = await command_parser.parse()

    if not result.valid:
        await message.reply(result.response)
        return

    count = result.params.get('count')
    description = result.params.get('description')

    # (!) edit service and repository
    # add tables for saving stats
    await service.add_tickets(message, count, description)
    await message.reply(gv.TICKETS_ADDED_TEXT)

    ##################################################################

    # if message.reply_to_message is None:
    #     await message.reply(gv.NO_REPLY_TEXT)
    #     return
    #
    # args = await get_command_args(message.text)
    #
    # if len(args) == 0:
    #     await message.reply(gv.WRONG_COMMAND_ARGUMENTS_TEXT)
    #     return
    #
    # arg = args[0]
    #
    # if not arg.isdigit():
    #     await message.reply(gv.WRONG_COMMAND_ARGUMENTS_TEXT)
    #     return
    #
    # if int(arg) == 0:
    #     await message.reply(gv.WRONG_COMMAND_ARGUMENTS_TEXT)
    #     return
    #
    # await service.add_tickets(message, int(arg))
    # await message.reply(gv.TICKETS_ADDED_TEXT)


@dp.message(Command("remove_tickets"))
async def delt(message: Message) -> None:
    pass


@dp.message(Command("set_tickets"))
async def sett(message: Message) -> None:
    pass


async def create_databases():
    os.makedirs(os.path.dirname(gv.rms.db_file_path), exist_ok=True)
    async with aiosqlite.connect(gv.rms.db_file_path) as db:
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


async def define_run_mode() -> RunMode:
    if len(sys.argv) <= 1:
        return RunMode.DEFAULT

    arg = sys.argv[1]

    if arg == RunMode.DEV.value:
        return RunMode.DEV
    elif arg == RunMode.PROD.value:
        return RunMode.PROD


async def define_rms(rm: RunMode) -> bool:
    if rm not in [RunMode.PROD, RunMode.DEV]:
        return False
    t = await get_run_mode_settings(rm)
    print(t)
    gv.rms = t
    print(gv.rms)
    return True


async def main() -> None:
    run_mode = await define_run_mode()
    valid_args = await define_rms(run_mode)

    if not valid_args:
        raise RuntimeError("THE PROGRAM WAS STARTED WITH INVALID COMMAND PARAMETERS!")

    await create_databases()

    bot = Bot(token=gv.rms.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp.message.middleware(SourceFilterMiddleware())

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
