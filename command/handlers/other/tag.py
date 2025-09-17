from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from command.parser.core.overload import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from model.types.custom.primitives import UserID
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(CL.tag.name))
async def tag(message: Message):
    og = CommandOverloadGroup([
        CommandOverload().add(glob.USER_ID_ARG, UserID)
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await message.answer(glob.COM_PARSER_FAILED)

    user_id = cpr.args[glob.USER_ID_ARG]
    await message.answer(
        text=f"[{glob.TAG_TEXT}](tg://user?id={user_id})",
        parse_mode=ParseMode.MARKDOWN
    )
