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
from utilities.comparser import CommandList as cl, CPRResponse as cprr, ParamType as pt, CommandParser
from utilities.globalvars import GlobalVariables as GV
from repository.Repository import Repository
from service.Service import Service
from utilities.runmode import RunMode
from utilities.func import get_random_permission_denied_message, get_run_mode_settings, get_db_setup_sql_script

service = Service()
dp = Dispatcher()


@dp.message(Command(cl.togglechat.name))
async def togglechat(message: Message) -> None:
    com_parser = CommandParser(
        message=message,
        creator_required=True
    )

    result = await com_parser.parse()

    if not result.valid:
        await _respond_invalid(message, result.response)
        return

    await service.toggle_chat_mode()
    status = 'enabled' if service.chat_mode else 'disabled'

    await message.reply(f'{GV.TOGGLE_CHAT_TEXT}: <b>{status}</b>', parse_mode=ParseMode.HTML)


@dp.message(Command(cl.sql.name))
async def sql(message: Message) -> None:
    # /sql <query:text>
    _query = 'query'

    com_parser = (CommandParser(
        message=message,
        creator_required=True)
                  .add_param(_query, pt.text))

    result = await com_parser.parse()

    if not result.valid:
        await _respond_invalid(message, result.response)
        return

    (executed, response) = await service.execute_sql(
        query=result.params.get(_query)
    )

    status = GV.SQL_SUCCESS_TEXT if executed else GV.SQL_FAILED_TEXT
    await message.reply(f'{status}\n\n{response}', parse_mode=None)


@dp.message(Command(cl.addt.name))
async def addt(message: Message) -> None:
    # <reply> /addt <count:pzint> [<description:text>]
    _count = 'count'
    _description = 'description'

    com_parser = (CommandParser(
        message=message,
        creator_required=True,
        replied=True)
                  .add_param(_count, pt.pzint)
                  .add_param(_description, pt.text))

    result = await com_parser.parse()

    if not result.valid:
        await _respond_invalid(message, result.response)
        return

    await service.add_tickets(
        user=message.reply_to_message.from_user,
        tickets_count=result.params.get(_count),
        description=result.params.get(_description)
    )

    await message.answer(GV.ADDT_TEXT)


@dp.message(Command(cl.delt.name))
async def delt(message: Message) -> None:
    # <reply> /delt <count:pzint> [<description:text>]
    _count = 'count'
    _description = 'description'

    com_parser = (CommandParser(
        message=message,
        creator_required=True,
        replied=True)
                  .add_param(_count, pt.pzint)
                  .add_param(_description, pt.text))

    result = await com_parser.parse()

    if not result.valid:
        await _respond_invalid(message, result.response)
        return

    await service.remove_tickets(
        user=message.reply_to_message.from_user,
        tickets_count=result.params.get(_count),
        description=result.params.get(_description)
    )

    await message.answer(GV.DELT_TEXT)


@dp.message(Command(cl.sett.name))
async def sett(message: Message) -> None:
    # <reply> /sett <count:int> [<description:text>]
    _count = 'count'
    _description = 'description'

    com_parser = (CommandParser(
        message=message,
        creator_required=True,
        replied=True)
                  .add_param(_count, pt.int)
                  .add_param(_description, pt.text))

    result = await com_parser.parse()

    if not result.valid:
        await _respond_invalid(message, result.response)
        return

    await service.set_tickets(
        user=message.reply_to_message.from_user,
        tickets_count=result.params.get(_count),
        description=result.params.get(_description)
    )

    await message.answer(GV.SETT_TEXT)


@dp.message(Command(cl.help.name))
async def help_(message: Message) -> None:
    # /help
    result = await CommandParser(message).parse()

    if not result.valid:
        await _respond_invalid(message, result.response)
        return

    await message.answer(GV.HELP_TEXT)


@dp.message(Command(cl.infm.name))
async def infm(message: Message) -> None:
    # [<reply>] /infm
    com_parser = CommandParser(
        message=message,
        replied=True,
        reply_optional=True
    )

    result = await com_parser.parse()

    if not result.valid:
        await _respond_invalid(message, result.response)
        return

    user = message.from_user \
        if message.reply_to_message is None \
        else message.reply_to_message.from_user

    response = await service.get_member_info(user)
    await message.answer(response, parse_mode=ParseMode.HTML)


@dp.message(Command(cl.bal.name))
async def bal(message: Message) -> None:
    # [<reply>] /bal
    com_parser = CommandParser(
        message=message,
        replied=True,
        reply_optional=True
    )

    result = await com_parser.parse()

    if not result.valid:
        await _respond_invalid(message, result.response)
        return

    user = message.from_user \
        if message.reply_to_message is None \
        else message.reply_to_message.from_user

    response = await service.get_member_tickets_count_info(user)
    await message.answer(response)


@dp.message(Command(cl.toptall.name))
async def toptall(message: Message) -> None:
    # /toptall
    result = await CommandParser(message).parse()

    if not result.valid:
        await _respond_invalid(message, result.response)
        return

    response = await service.get_tickets_top(message.from_user)
    await message.answer(response)


@dp.message(Command(cl.topt.name))
async def topt(message: Message) -> None:
    # /topt [<size:zint>]
    _size = 'size'

    result = await CommandParser(message).add_param(_size, pt.zint).parse()

    if not result.valid:
        await _respond_invalid(message, result.response)
        return

    response = await service.get_tickets_top_by_size(
        user=message.from_user,
        size=result.params.get(_size)
    )

    await message.answer(response)


@dp.message()
async def gur_mode(message: Message) -> None:
    if not service.chat_mode:
        return

    if not message.content_type == 'text':
        return

    com_parser = CommandParser(
        message=message,
        creator_required=True
    )

    result = await com_parser.parse()

    if not result.valid:
        await _respond_invalid(message, result.response)
        return

    await service.bot.send_message(
        chat_id=GV.rms.group_chat_id,
        text=message.text
    )


async def _create_databases():
    os.makedirs(os.path.dirname(GV.rms.db_file_path), exist_ok=True)
    async with aiosqlite.connect(GV.rms.db_file_path) as db:
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

    GV.rms = await get_run_mode_settings(rm)
    return True


async def _define_service() -> None:
    global service
    service = Service(Repository(GV.rms.db_file_path))


async def _respond_invalid(message: Message, response: cprr):
    out_message = await get_random_permission_denied_message() \
        if response == cprr.not_creator else response

    await message.reply(out_message)


async def main() -> None:
    run_mode = await _define_run_mode()
    valid_args = await _define_rms(run_mode)

    if not valid_args:
        raise RuntimeError(GV.VALID_ARGS_TEXT)

    await _define_service()
    await _create_databases()

    service.bot = Bot(token=GV.rms.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp.message.middleware(SourceFilterMiddleware())

    await dp.start_polling(service.bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
