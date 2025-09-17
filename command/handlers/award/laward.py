import functools

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from service import service_core as service
from command.util.validations import validate_message
from command.parser.core import cog
from command.parser.core.parser import CommandParser
from component.paged_viewer import page_generators
from component.paged_viewer.paged_viewer import PagedViewer
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(CL.laward.name))
async def laward(message: Message):
    if not await validate_message(message):
        return

    cpr = await CommandParser(message, cog.pure()).parse()

    if not cpr.valid:
        return await message.answer(glob.COM_PARSER_FAILED)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    viewer = PagedViewer(
        title=glob.LAWARD_TITLE,
        data_extractor=functools.partial(service.laward, target_member.user_id),
        page_generator=page_generators.laward,
        page_message=message,
        parse_mode=ParseMode.HTML
    )

    operation_id = await service.som().reg(
        func=functools.partial(lambda: viewer),
        asynchronous=False
    )

    await viewer.view(operation_id)
