from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from service import service_core as service
from command.util.validations import validate_message
from component.keyboards.keyboards import hide_keyboard
from command.parser.core import cog
from command.parser.core.parser import CommandParser
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(CL.infm.name))
async def infm(message: Message):
    if not await validate_message(message):
        return

    cpr = await CommandParser(message, cog.pure()).parse()

    if not cpr.valid:
        return await message.answer(glob.COM_PARSER_FAILED)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    await message.answer(
        text=await service.infm(target_member),
        parse_mode=ParseMode.HTML,
        reply_markup=await hide_keyboard()
    )
