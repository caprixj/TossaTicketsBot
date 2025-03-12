import asyncio
import logging
import os
import sys
import utilities.globals as glob

import aiosqlite
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

import comparser.standard_overloads as sol
from comparser.results.CommandHandlerResult import CommandHandlerResult
from comparser.CommandParser import CommandParser
from comparser.Overload import Overload
from comparser.enums.ParamType import ParamType as pt
from comparser.enums.CommandList import CommandList as cl
from comparser.enums.ResultErrorMessages import ResultErrorMessages
from middleware.SourceFilterMiddleware import SourceFilterMiddleware
from repository.Repository import Repository
from service.Service import Service
from utilities.run_mode import RunMode
from utilities.func import get_random_permission_denied_message, get_run_mode_settings, get_db_setup_sql_script

service = Service()
dp = Dispatcher()


@dp.message(Command(cl.sql.name))
async def sql(message: Message) -> None:
    # /sql <query:text>
    o = Overload(creator_filter=True).add_param(sol.QUERY, pt.text)

    cp = CommandParser(message, o)
    result = await cp.parse()

    if not result.valid:
        await _respond_invalid(message, result.error_message)
        return

    (executed, response) = await service.execute_sql(
        query=result.params.get(sol.QUERY)
    )

    status = glob.SQL_SUCCESS_TEXT if executed else glob.SQL_FAILED_TEXT
    await message.reply(f'{status}\n\n{response}', parse_mode=None)


@dp.message(Command(cl.addt.name))
async def addt(message: Message) -> None:
    result = await count_handler(
        message=message,
        count_type=pt.pzint,
        creator_filter=True
    )

    if not result.valid:
        return

    await service.add_tickets(
        member=result.target_member,
        tickets_count=result.get_param(sol.COUNT),
        description=result.get_param(sol.DESCRIPTION)
    )

    await message.answer(glob.ADDT_TEXT)


@dp.message(Command(cl.delt.name))
async def delt(message: Message) -> None:
    result = await count_handler(
        message=message,
        count_type=pt.pzint,
        creator_filter=True
    )

    if not result.valid:
        return

    await service.delete_tickets(
        member=result.target_member,
        tickets_count=result.get_param(sol.COUNT),
        description=result.get_param(sol.DESCRIPTION)
    )

    await message.answer(glob.DELT_TEXT)


@dp.message(Command(cl.sett.name))
async def sett(message: Message) -> None:
    result = await count_handler(
        message=message,
        count_type=pt.int,
        creator_filter=True
    )

    if not result.valid:
        return

    await service.set_tickets(
        member=result.target_member,
        tickets_count=result.get_param(sol.COUNT),
        description=result.get_param(sol.DESCRIPTION)
    )

    await message.answer(glob.SETT_TEXT)


@dp.message(Command(cl.help.name))
async def help_(message: Message) -> None:
    await message.answer(glob.HELP_TEXT)


@dp.message(Command(cl.topt.name))
async def topt(message: Message) -> None:
    # /topt
    o_no_size = Overload(name='no-size')

    # /topt <size:zint>
    o_size = Overload(name='size').add_param(sol.SIZE, pt.zint)

    cpr = await CommandParser(message, o_no_size, o_size).parse()

    if not cpr.valid:
        await _respond_invalid(message, cpr.error_message)
        return

    async def _match_overload():
        return await service.get_tickets_top() if cpr.overload.name == o_no_size.name \
            else await service.get_tickets_top_by_size(cpr.params.get(sol.SIZE))

    await service.validate_member(message.from_user)
    response = await _match_overload()
    await message.answer(response)


@dp.message(Command(cl.bal.name))
async def bal(message: Message) -> None:
    result = await empty_handler(message)

    if not result.valid:
        return

    response = await service.get_member_tickets_count_info(result.target_member)
    await message.answer(response)


@dp.message(Command(cl.infm.name))
async def infm(message: Message) -> None:
    result = await empty_handler(message)

    if not result.valid:
        return

    response = await service.get_member_info(result.target_member.user_id)
    await message.answer(response, parse_mode=ParseMode.HTML)


@dp.message(Command(cl.ttime.name))
async def ttime(message: Message) -> None:
    pass


@dp.message(Command(cl.tpay.name))
async def tpay(message: Message) -> None:
    pass


@dp.message(Command(cl.tkick.name))
async def tkick(message: Message) -> None:
    pass


@dp.message(Command(cl.tmute.name))
async def tmute(message: Message) -> None:
    pass


@dp.message(Command(cl.tban.name))
async def tban(message: Message) -> None:
    pass


@dp.message(Command(cl.demute.name))
async def demute(message: Message) -> None:
    pass


@dp.message(Command(cl.deban.name))
async def deban(message: Message) -> None:
    pass


# [<reply>] /command
# /command <username:username>
# /command <user_id:pzint>
async def empty_handler(message: Message) -> CommandHandlerResult:
    overloads = [
        await sol.reply_empty(reply_optional=True),
        await sol.username_empty(),
        await sol.user_id_empty()
    ]

    cp = CommandParser(message, *overloads)
    cpr = await cp.parse()

    if not cpr.valid:
        await _respond_invalid(message, cpr.error_message)
        return CommandHandlerResult()

    user = message.from_user \
        if message.reply_to_message is None \
        else message.reply_to_message.from_user

    target_member = await service.get_member_by_cpr(cpr, user)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED_TEXT)
        return CommandHandlerResult()

    return CommandHandlerResult(target_member, cpr, valid=True)


# <reply> /command <count:any> [<description:text>]
# /command <username:username> <count:any> [<description:text>]
# /command <user_id:pzint> <count:any> [<description:text>]
async def count_handler(message: Message, count_type: pt, creator_filter: bool = False) -> CommandHandlerResult:
    overloads = [
        await sol.reply_count(count_type=count_type, creator_filter=creator_filter),
        await sol.username_count(pt.pzint, creator_filter=creator_filter),
        await sol.user_id_count(pt.pzint, creator_filter=creator_filter)
    ]

    cp = CommandParser(message, *overloads)
    cpr = await cp.parse()

    if not cpr.valid:
        await _respond_invalid(message, cpr.error_message)
        return CommandHandlerResult()

    user = message.reply_to_message.from_user if message.reply_to_message is not None else None
    target_member = await service.get_member_by_cpr(cpr, user)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED_TEXT)
        return CommandHandlerResult()

    return CommandHandlerResult(target_member, cpr, valid=True)


async def _create_databases():
    os.makedirs(os.path.dirname(glob.rms.db_file_path), exist_ok=True)
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        for query in await get_db_setup_sql_script():
            await db.execute(query)
            await db.commit()


async def _define_run_mode() -> RunMode:
    if len(sys.argv) <= 1:
        return RunMode.DEFAULT

    arg = sys.argv[1]

    if arg == RunMode.DEV.value:
        return RunMode.DEV
    elif arg == RunMode.PROD.value:
        return RunMode.PROD


async def _define_rms(rm: RunMode) -> bool:
    if rm not in [RunMode.PROD, RunMode.DEV]:
        return False

    glob.rms = await get_run_mode_settings(rm)
    return True


async def _define_service() -> None:
    global service
    service = Service(Repository(glob.rms.db_file_path))


async def _respond_invalid(message: Message, response: ResultErrorMessages):
    out_message = await get_random_permission_denied_message() \
        if response == ResultErrorMessages.not_creator else response

    await message.reply(out_message)


async def main() -> None:
    run_mode = await _define_run_mode()
    valid_args = await _define_rms(run_mode)

    if not valid_args:
        raise RuntimeError(glob.VALID_ARGS_TEXT)

    await _define_service()
    await _create_databases()

    service.bot = Bot(token=glob.rms.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp.message.middleware(SourceFilterMiddleware())

    await dp.start_polling(service.bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
