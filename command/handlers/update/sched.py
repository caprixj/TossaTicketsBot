from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from command.util.crv import reply_by_crv
from service import scheduling
from command.parser.core.overload import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from command.util.validations import validate_message
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(CL.sched.name))
async def sched(message: Message, bot: Bot):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
        CommandOverload(admin=True)
    ])
    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await reply_by_crv(message, cpr)

    await scheduling.daily_sched(bot=bot, tbox=True)
    await message.answer(glob.DAILY_SCHEDULE_DONE)
