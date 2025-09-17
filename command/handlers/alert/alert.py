from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from service import service_core as service
from command.util.validations import validate_message
from command.parser.core.overload import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(CL.alert.name))
async def alert(message: Message):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
        CommandOverload(public=True)
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        if cpr.public_violation:
            await message.answer(glob.PUBLIC_VIOLATION)
        else:
            await message.answer(glob.COM_PARSER_FAILED)
        return

    if await service.get_sfs_alert_message(message.chat.id) is None:
        sent_message = await message.answer(glob.SFS_ALERT_TEXT)
        await service.pin_sfs_alert(message.chat.id, sent_message)
    else:
        await message.reply(glob.SFS_ALERT_FAILED)


@router.message(Command(CL.unalert.name))
async def unalert(message: Message):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
        CommandOverload(public=True)
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        if cpr.public_violation:
            await message.answer(glob.PUBLIC_VIOLATION)
        else:
            await message.answer(glob.COM_PARSER_FAILED)
        return

    pin_message = await service.get_sfs_alert_message(message.chat.id)
    if pin_message is None:
        await message.reply(glob.SFS_UNALERT_FAILED)
    else:
        await service.unpin_sfs_alert(pin_message)
        await message.reply(glob.SFS_UNALERT_TEXT)
