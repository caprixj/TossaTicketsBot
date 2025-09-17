from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from command.util.crv import reply_by_crv
from service import service_core as service
from command.parser.core import cog
from command.parser.core.parser import CommandParser
from command.util.validations import validate_message
from model.types.custom.bounds import EmployeePosition
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(CL.hire.name))
async def hire(message: Message):
    if not await validate_message(message):
        return

    og = cog.a1_any(a1_name=glob.EMPLOYEE_ARG, a1_type=EmployeePosition, admin_required=True)
    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await reply_by_crv(message, cpr)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    employee_position = cpr.args[glob.EMPLOYEE_ARG]

    if await service.is_hired(target_member.user_id, employee_position):
        return await message.answer(glob.MEMBER_ALREADY_HIRED)

    response = await service.hire(target_member, employee_position)

    await message.answer(response)
