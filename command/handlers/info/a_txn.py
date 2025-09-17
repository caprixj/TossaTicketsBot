import functools

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from model.database.member import Member
from service import service_core as service
from command.util.validations import validate_message
from command.parser.core import cog
from command.parser.core.parser import CommandParser
from component.paged_viewer import page_generators
from component.paged_viewer.paged_viewer import PagedViewer
from command.parser.types.command_list import CommandList as CL
from utils import funcs

router = Router()


@router.message(Command(CL.txn.name, CL.atxn.name))
async def a_txn(message: Message):
    if not await validate_message(message):
        return

    com = funcs.get_command(message)
    target_member: Member

    if com == CL.atxn.name:
        cpr = await CommandParser(message, cog.pure(creator_required=True)).parse()

        if not cpr.valid:
            return await message.answer(glob.COM_PARSER_FAILED)

        target_member = await service.get_target_member(cpr)

        if target_member is None:
            return await message.answer(glob.GET_MEMBER_FAILED)
    else:  # if co.command == cl.txn.name
        target_member = await service.get_member(message.from_user.id)

    viewer = PagedViewer(
        title=f'{glob.TXN_TITLE}\n{glob.MEMBER_RES}: {funcs.get_formatted_name(target_member)}',
        data_extractor=functools.partial(service.txn, target_member.user_id),
        page_generator=page_generators.txn,
        page_message=message,
        start_text=glob.TXN_START_TEXT,
        parse_mode=ParseMode.HTML
    )

    operation_id = await service.som().reg(
        func=functools.partial(lambda: viewer),
        asynchronous=False
    )

    await viewer.view(operation_id)
