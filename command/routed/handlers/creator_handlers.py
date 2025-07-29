import random

from aiogram import Router, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

import resources.glob as glob
from command.parser.keyboards.keyboards import hide_keyboard
from model.database import AwardMember
from resources import funcs
from service import service_core as service, scheduling
from service.price_manager import reset_prices
from command.parser.core import cog
from command.parser.core.overload import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from command.parser.results.parser_result import CommandParserResult
from command.routed.util.validations import validate_message
from model.types.ticketonomics_types import BaseText, RealTickets, PNRealTickets, SID, EmployeePosition, Username, UserID, ChatID, \
    ConstArg
from command.parser.types.com_list import CommandList as cl

from resources.rands import crv_messages

router = Router()


@router.message(Command(commands=[cl.sql.name, cl.sqls.name]))
async def sql(message: Message):
    og = CommandOverloadGroup([
        # /c <query:text>
        CommandOverload().add(glob.QUERY_ARG, BaseText)
    ], creator=True)

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await _reply_by_crv(message, cpr)

    (executed, response) = await service.sql_execute(
        query=cpr.args[glob.QUERY_ARG],
        many=funcs.get_command(message) == cl.sqls.name
    )

    status = glob.SQL_SUCCESS if executed else glob.SQL_FAILED
    await message.reply(
        text=f'{status}\n\n{response}',
        parse_mode=None,
        reply_markup=hide_keyboard()
    )


@router.message(Command(cl.sqlf.name))
async def sqlf(message: Message):
    og = CommandOverloadGroup([
        CommandOverload(reply=True, creator=True)
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await _reply_by_crv(message, cpr)

    reply = message.reply_to_message
    if not reply or not reply.document:
        return await message.answer(glob.NOT_TXT_FILE_ERROR)

    doc = reply.document
    if not (doc.mime_type == 'text/plain' or doc.file_name.lower().endswith('.txt')):
        return await message.answer(glob.NOT_TXT_FILE_ERROR)

    file = await message.bot.get_file(doc.file_id)
    stream = await message.bot.download_file(file.file_path)
    data: bytes = stream.read()
    query = data.decode('utf-8')

    executed, response = await service.sql_execute(
        query=query,
        many=True
    )

    status = glob.SQL_SUCCESS if executed else glob.SQL_FAILED
    await message.reply(
        text=f'{status}\n\n{response}',
        parse_mode=None,
        reply_markup=hide_keyboard()
    )


@router.message(Command(cl.addt.name))
async def addt(message: Message):
    cpr = await CommandParser(message, cog.tickets(PNRealTickets, creator_required=True)).parse()

    if not cpr.valid:
        return await _reply_by_crv(message, cpr)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    await service.addt(
        member=target_member,
        tickets=cpr.args[glob.TICKETS_ARG],
        description=cpr.args.get(glob.DESCRIPTION_ARG, None)
    )

    await message.answer(
        f'{glob.ADDT_TEXT}'
        f'\n{glob.MEMBER_RES}: {funcs.get_formatted_name(target_member)}'
        f'\n{glob.AMOUNT_RES}: +{cpr.args[glob.TICKETS_ARG] / 100:.2f}'
    )


@router.message(Command(cl.delt.name))
async def delt(message: Message):
    cpr = await CommandParser(message, cog.tickets(PNRealTickets, creator_required=True)).parse()

    if not cpr.valid:
        return await _reply_by_crv(message, cpr)

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


@router.message(Command(cl.sett.name))
async def sett(message: Message):
    cpr = await CommandParser(message, cog.tickets(RealTickets, creator_required=True)).parse()

    if not cpr.valid:
        return await _reply_by_crv(message, cpr)

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


@router.message(Command(cl.award.name))
async def award(message: Message):
    if not await validate_message(message):
        return

    og = cog.a1_any(a1_name=glob.AWARD_ID_ARG, a1_type=SID, creator_required=True)
    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await _reply_by_crv(message, cpr)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    award_ = await service.get_award(cpr)

    if award_ is None:
        return await message.answer(glob.GET_AWARD_FAILED)

    am = AwardMember(
        award_id=award_.award_id,
        owner_id=target_member.user_id
    )

    if await service.issue_award(am):
        response = await service.award(target_member, award_, am.issue_date)
        await message.answer(
            text=response,
            reply_markup=hide_keyboard(),
            parse_mode=ParseMode.HTML
        )
    else:
        await message.answer(glob.AWARD_DUPLICATE)


@router.message(Command(cl.hire.name))
async def hire(message: Message):
    if not await validate_message(message):
        return

    og = cog.a1_any(a1_name=glob.EMPLOYEE_ARG, a1_type=EmployeePosition, creator_required=True)
    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await _reply_by_crv(message, cpr)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    employee_position = cpr.args[glob.EMPLOYEE_ARG]

    if await service.is_hired(target_member.user_id, employee_position):
        return await message.answer(glob.MEMBER_ALREADY_HIRED)

    response = await service.hire(target_member, employee_position)

    await message.answer(response)


@router.message(Command(cl.fire.name))
async def fire(message: Message):
    if not await validate_message(message):
        return

    og = cog.a1_any(a1_name=glob.EMPLOYEE_ARG, a1_type=EmployeePosition, creator_required=True)
    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await _reply_by_crv(message, cpr)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    employee_position = cpr.args[glob.EMPLOYEE_ARG]

    fired = await service.fire(target_member.user_id, employee_position)
    await message.answer(
        f'{glob.MEMBER_FIRED if fired else glob.MEMBER_ALREADY_FIRED}'
        f'\n{glob.MEMBER_RES}: {funcs.get_formatted_name(target_member)}'
        f'\n{glob.POSITION_RES}: {await service.get_job_name(employee_position)}'
    )


@router.message(Command(cl.resetprice.name))
async def reset_price(message: Message):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
        CommandOverload(creator=True)
    ])
    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await _reply_by_crv(message, cpr)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    await reset_prices()
    await message.answer(glob.RESET_PRICE_COMMAND_DONE)


@router.message(Command(cl.sched.name))
async def sched(message: Message):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
        CommandOverload(creator=True)
    ])
    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await _reply_by_crv(message, cpr)

    await scheduling.daily_sched()
    await message.answer(glob.DAILY_SCHEDULE_DONE)


@router.message(Command(cl.unreg.name))
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
        CommandOverload(otype=glob.BAN_ARG, reply=True)
        .add(glob.BAN_ARG, ConstArg),

        # /c ban <username:username>
        CommandOverload(otype=glob.BAN_ARG)
        .add(glob.BAN_ARG, ConstArg)
        .add(glob.USERNAME_ARG, Username),

        # /c ban <user_id:userid>
        CommandOverload(otype=glob.BAN_ARG)
        .add(glob.BAN_ARG, ConstArg)
        .add(glob.USER_ID_ARG, UserID)
    ], creator=True)

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await _reply_by_crv(message, cpr)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    if target_member.user_id == glob.CREATOR_USER_ID:
        return await message.answer(glob.UNREG_CREATOR_ERROR)

    await service.unreg(target_member, otype=cpr.overload.otype)
    await message.answer(f'{glob.UNREG_TEXT}\n{glob.MEMBER_RES}: {funcs.get_formatted_name(target_member)}')


@router.message(Command(cl.db.name))
async def db(message: Message):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
        CommandOverload(creator=True)
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await _reply_by_crv(message, cpr)

    await message.answer_document(
        FSInputFile(glob.rms.db_file_path)
    )


@router.message(Command(cl.msg.name))
async def msg(message: Message, bot: Bot):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
        CommandOverload(reply=True).add(glob.CHAT_ID_ARG, ChatID)
    ], creator=True)

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await _reply_by_crv(message, cpr)

    await bot.send_message(
        chat_id=cpr.args[glob.CHAT_ID_ARG],
        text=message.reply_to_message.text,
        parse_mode=ParseMode.MARKDOWN
    )


""" Private """


async def _reply_by_crv(message: Message, cpr: CommandParserResult):
    out = _get_random_crv_message() \
        if cpr.creator_violation else glob.COM_PARSER_FAILED

    await message.reply(out)


def _get_random_crv_message() -> str:
    return crv_messages[random.randint(0, len(crv_messages) - 1)]
