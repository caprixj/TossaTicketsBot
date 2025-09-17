from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from service import service_core as service
from component.keyboards.keyboards import hide_keyboard
from command.parser.core.overload import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from model.types.custom.primitives import PNRealTickets
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(CL.p.name))
async def p(message: Message):
    og = CommandOverloadGroup([
        # /p <price:pnreal>
        CommandOverload().add(glob.PRICE_ARG, PNRealTickets)
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await message.answer(glob.COM_PARSER_FAILED)

    response = await service.p(cpr.args[glob.PRICE_ARG])
    await message.answer(
        text=response,
        reply_markup=await hide_keyboard()
    )
