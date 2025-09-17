from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from command.util.crv import reply_by_crv
from component.keyboards.keyboards import hide_keyboard
from utils import funcs
from service import service_core as service
from command.parser.core.overload import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from model.types.custom.primitives import BaseText
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(commands=[CL.sql.name, CL.sqls.name]))
async def sql(message: Message):
    og = CommandOverloadGroup([
        # /c <query:text>
        CommandOverload().add(glob.QUERY_ARG, BaseText)
    ], admin=True)

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await reply_by_crv(message, cpr)

    (executed, response) = await service.sql_execute(
        query=cpr.args[glob.QUERY_ARG],
        many=funcs.get_command(message) == CL.sqls.name
    )

    status = glob.SQL_SUCCESS if executed else glob.SQL_FAILED
    await message.reply(
        text=f'{status}\n\n{response}',
        parse_mode=None,
        reply_markup=await hide_keyboard()
    )


@router.message(Command(CL.sqlf.name))
async def sqlf(message: Message):
    og = CommandOverloadGroup([
        CommandOverload(reply=True, admin=True)
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await reply_by_crv(message, cpr)

    reply = message.reply_to_message
    if not reply or not reply.document:
        return await message.answer(glob.NOT_TXT_FILE_ERROR)

    doc = reply.document
    if not (doc.mime_type == 'text/plain' or doc.file_name.lower().endswith('.txt')):
        return await message.answer(glob.NOT_TXT_FILE_ERROR)

    file = await message.bot.get_file(doc.file_id)
    stream = await message.bot.download_file(file.file_path)
    data: bytes = stream.read()
    query = data.decode('utf-8')

    executed, response = await service.sql_execute(
        query=query,
        many=True
    )

    status = glob.SQL_SUCCESS if executed else glob.SQL_FAILED
    await message.reply(
        text=f'{status}\n\n{response}',
        parse_mode=None,
        reply_markup=await hide_keyboard()
    )