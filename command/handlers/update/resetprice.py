from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from command.util.crv import reply_by_crv
from service import service_core as service
from service.price_manager import reset_prices
from command.parser.core.overload import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from command.util.validations import validate_message
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(CL.resetprice.name))
async def reset_price(message: Message):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
        CommandOverload(admin=True)
    ])
    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await reply_by_crv(message, cpr)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    await reset_prices()
    await message.answer(glob.RESET_PRICE_COMMAND_DONE)
