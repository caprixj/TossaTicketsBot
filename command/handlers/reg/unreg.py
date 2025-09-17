from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from command.util.crv import reply_by_crv
from model.types.custom.flags import BanFlag
from utils import funcs
from service import service_core as service
from command.parser.core.overload import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from command.util.validations import validate_message
from model.types.custom.primitives import Username, UserID
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(CL.unreg.name))
async def unreg(message: Message):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
        # <reply> /c
        CommandOverload(reply=True),
        # /c <username:username>
        CommandOverload().add(glob.USERNAME_ARG, Username),
        # /c <user_id:userid>
        CommandOverload().add(glob.USER_ID_ARG, UserID),
        # <reply> /c ban
        CommandOverload(otype=glob.BAN_FLAG, reply=True).flag(BanFlag),
        # /c ban <username:username>
        CommandOverload(otype=glob.BAN_FLAG).flag(BanFlag).add(glob.USERNAME_ARG, Username),
        # /c ban <user_id:userid>
        CommandOverload(otype=glob.BAN_FLAG).flag(BanFlag).add(glob.USER_ID_ARG, UserID)
    ], admin=True)

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await reply_by_crv(message, cpr)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    if glob.rms.is_admin(target_member.user_id):
        return await message.answer(glob.UNREG_CREATOR_ERROR)

    await service.unreg(target_member, otype=cpr.overload.otype)
    await message.answer(f'{glob.UNREG_TEXT}\n{glob.MEMBER_RES}: {funcs.get_formatted_name(target_member)}')
