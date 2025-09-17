from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from command.util.crv import reply_by_crv
from utils import funcs
from service import service_core as service
from command.parser.core import cog
from command.parser.core.parser import CommandParser
from model.types.custom.primitives import RealTickets
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(CL.sett.name))
async def sett(message: Message):
    cpr = await CommandParser(message, cog.tickets(RealTickets, admin_required=True)).parse()

    if not cpr.valid:
        return await reply_by_crv(message, cpr)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    transfer_amount = await service.sett(
        member=target_member,
        tickets=cpr.args[glob.TICKETS_ARG],
        description=cpr.args.get(glob.DESCRIPTION_ARG, None)
    )

    sign = '+' if transfer_amount > 0 else ''
    await message.answer(
        f'{glob.SETT_TEXT}'
        f'\n{glob.MEMBER_RES}: {funcs.get_formatted_name(target_member)}'
        f'\n{glob.AMOUNT_RES}: {sign}{transfer_amount / 100:.2f}'
    )
