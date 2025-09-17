from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from command.util.crv import reply_by_crv
from utils import funcs
from service import service_core as service
from command.parser.core import cog
from command.parser.core.parser import CommandParser
from model.types.custom.primitives import PNRealTickets
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(CL.delt.name))
async def delt(message: Message):
    cpr = await CommandParser(message, cog.tickets(PNRealTickets, admin_required=True)).parse()

    if not cpr.valid:
        return await reply_by_crv(message, cpr)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    await service.delt(
        member=target_member,
        tickets=cpr.args[glob.TICKETS_ARG],
        description=cpr.args.get(glob.DESCRIPTION_ARG, None)
    )

    await message.answer(
        f'{glob.DELT_TEXT}'
        f'\n{glob.MEMBER_RES}: {funcs.get_formatted_name(target_member)}'
        f'\n{glob.AMOUNT_RES}: -{cpr.args[glob.TICKETS_ARG] / 100:.2f}'
    )