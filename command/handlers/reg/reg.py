from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from command.util.crv import get_random_crv_message
from service import service_core as service
from command.parser.core.overload import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from command.parser.types.command_list import CommandList as CL
from command.parser.types.target_type import CommandTargetType as CTT
from utils import funcs

router = Router()


@router.message(Command(CL.reg.name))
async def reg(message: Message, bot: Bot):
    og = CommandOverloadGroup([
        # /reg
        CommandOverload(),
        # <reply> /reg
        CommandOverload(reply=True)
    ], public=True)

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        if cpr.public_violation:
            await message.answer(glob.PUBLIC_VIOLATION)
        else:
            await message.answer(glob.COM_PARSER_FAILED)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        response = await service.reg_member(
            sender=message.from_user,
            target=message.reply_to_message.from_user if cpr.overload.target_type == CTT.REPLY else message.from_user,
            anchor_=message.chat.id
        )

        if not response and not glob.rms.is_admin(message.from_user.id):
            return message.answer(get_random_crv_message())

        reply_uid = message.reply_to_message.from_user.id \
            if message.reply_to_message is not None \
            else None

        await funcs.broadcast_message(
            bot=bot,
            text=(f'chat id: {message.chat.id}\n'
                  f'from-user id: {message.from_user.id}\n'
                  f'reply-user id: {reply_uid}'),
            admins=True
        )

        await message.answer(glob.REG_SUCCESS)

    else:
        if cpr.overload.target_type == CTT.NONE:
            await service.update_member(message.from_user, target_member)
            await message.answer(glob.REG_DENIED_CTT_NONE)
        elif cpr.overload.target_type == CTT.REPLY:
            await service.update_member(message.reply_to_message.from_user, target_member)
            await message.answer(glob.REG_DENIED_CTT_REPLY)
