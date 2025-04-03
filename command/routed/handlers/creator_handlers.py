import random

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

import resources.const.glob as glob
from model.database.award_member import AwardMemberJunction
from resources.funcs import funcs
from service import service_core as service
from command.parser.core import cog
from command.parser.core.overload import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from command.parser.results.parser_result import CommandParserResult
from command.routed.handlers.validations import validate_message
from model.types.ticketonomics_types import Text, Real, PNReal, SID
from command.parser.types.com_list import CommandList as cl

from resources.const.rands import crv_messages

router = Router()


@router.message(Command(cl.sql.name))
async def sql(message: Message):
    og = CommandOverloadGroup(
        # /sql <query:text>
        overloads=[CommandOverload().add(glob.QUERY_ARG, Text)],
        creator_required=True
    )

    cpr = CommandParser(message, og).parse()

    if not cpr.valid:
        await _reply_by_crv(message, cpr)
        return

    (executed, response) = await service.execute_sql(
        query=cpr.args[glob.QUERY_ARG]
    )

    status = glob.SQL_SUCCESS if executed else glob.SQL_FAILED
    await message.reply(f'{status}\n\n{response}', parse_mode=None)


@router.message(Command(cl.addt.name))
async def addt(message: Message):
    cpr = CommandParser(message, cog.tickets(PNReal, creator_required=True)).parse()

    if not cpr.valid:
        await _reply_by_crv(message, cpr)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED)
        return

    await service.addt(
        member=target_member,
        tickets=cpr.args[glob.TICKETS_ARG],
        description=cpr.args.get(glob.DESCRIPTION_ARG, None)
    )

    await message.answer(glob.ADDT_TEXT)


@router.message(Command(cl.delt.name))
async def delt(message: Message):
    cpr = CommandParser(message, cog.tickets(PNReal, creator_required=True)).parse()

    if not cpr.valid:
        await _reply_by_crv(message, cpr)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED)
        return

    await service.delt(
        member=target_member,
        tickets=cpr.args[glob.TICKETS_ARG],
        description=cpr.args.get(glob.DESCRIPTION_ARG, None)
    )

    await message.answer(glob.DELT_TEXT)


@router.message(Command(cl.sett.name))
async def sett(message: Message):
    cpr = CommandParser(message, cog.tickets(Real, creator_required=True)).parse()

    if not cpr.valid:
        await _reply_by_crv(message, cpr)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED)
        return

    await service.sett(
        member=target_member,
        tickets=cpr.args[glob.TICKETS_ARG],
        description=cpr.args.get(glob.DESCRIPTION_ARG, None)
    )

    await message.answer(glob.SETT_TEXT)


# @router.page_message(Command(cl.sfs.name))
# async def sfs(page_message: Message):
#     og = CommandOverloadGroup(
#         # /sfs <page_message:text>
#         overloads=[CommandOverload().add(glob.MESSAGE_ARG, Text)],
#         creator_required=True
#     )
#
#     cpr = CommandParser(page_message, og).parse()
#
#     if not cpr.valid:
#         await _reply_by_crv(page_message, cpr)
#         return
#
#     await service.bot.send_message(
#         chat_id=glob.rms.group_chat_id,
#         text=cpr.args[glob.MESSAGE_ARG]
#     )
#
#
# @router.page_message(Command(cl.db.name))
# async def db(page_message: Message) -> None:
#     og = CommandOverloadGroup(
#         # /db
#         overloads=[CommandOverload()],
#         creator_required=True
#     )
#
#     cpr = CommandParser(page_message, og).parse()
#
#     if not cpr.valid:
#         await _reply_by_crv(page_message, cpr)
#         return
#
#     await service.bot.send_document(
#         chat_id=page_message.chat.id,
#         document=FSInputFile(glob.rms.db_file_path)
#     )


@router.message(Command(cl.award.name))
async def award(message: Message):
    if not await validate_message(message):
        return

    og = cog.a1_any(a1_name=glob.AWARD_ID_ARG, a1_type=SID, creator_required=True)
    cpr = CommandParser(message, og).parse()

    if not cpr.valid:
        await message.answer(glob.COM_PARSER_FAILED)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED)
        return

    award_ = await service.get_award(cpr)

    if award_ is None:
        await message.answer(glob.GET_AWARD_FAILED)
        return

    am = AwardMemberJunction(
        award_id=award_.award_id,
        owner_id=target_member.user_id
    )

    if await service.issue_award(am):
        if award_.payment > 0:
            await service.pay_award(
                member=target_member,
                payment=award_.payment,
                description=award_.award_id
            )

        payment = f'\nвиплата: <b>{award_.payment:.2f} tc</b>' \
            if award_.payment > 0 else str()

        award_text = (f"{glob.AWARD_SUCCESS}"
                      f"\n\n<b>{award_.name}</b>"
                      f"\n\nid: <b>{award_.award_id}</b>"
                      f"{payment}"
                      f"\nвидано: <b>{am.issue_date}</b>"
                      f"\n\n<b>історія</b>: <i>{award_.description}</i>")
        await message.answer(award_text, parse_mode=ParseMode.HTML)
    else:
        await message.answer(glob.AWARD_DUPLICATE)


""" Private """


async def _reply_by_crv(message: Message, cpr: CommandParserResult):
    out = _get_random_crv_message() \
        if cpr.creator_required_violation else glob.COM_PARSER_FAILED

    await message.reply(out)


def _get_random_crv_message() -> str:
    return crv_messages[random.randint(0, len(crv_messages) - 1)]
