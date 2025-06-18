import random

from aiogram import Router, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

import resources.const.glob as glob
from command.parser.keyboards.keyboards import hide_keyboard
from model.database import AwardMember
from resources.funcs import funcs
from resources.funcs.funcs import get_formatted_name
from service import service_core as service, scheduling
from service.price_manager import reset_prices
from command.parser.core import cog
from command.parser.core.overload import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from command.parser.results.parser_result import CommandParserResult
from command.routed.util.validations import validate_message
from model.types.ticketonomics_types import BaseText, Real, PNReal, SID, EmployeePosition, Username, UserID, ChatID, \
    Text4096
from command.parser.types.com_list import CommandList as cl

from resources.const.rands import crv_messages

router = Router()


@router.message(Command(commands=[cl.sql.name, cl.sqls.name]))
async def sql(message: Message):
    og = CommandOverloadGroup(
        # /c <query:text>
        overloads=[CommandOverload().add(glob.QUERY_ARG, BaseText)],
        creator=True
    )

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


@router.message(Command(cl.addt.name))
async def addt(message: Message):
    cpr = await CommandParser(message, cog.tickets(PNReal, creator_required=True)).parse()

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

    await message.answer(f'{glob.ADDT_TEXT}\nmember: {get_formatted_name(target_member)}')


@router.message(Command(cl.delt.name))
async def delt(message: Message):
    cpr = await CommandParser(message, cog.tickets(PNReal, creator_required=True)).parse()

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

    await message.answer(f'{glob.DELT_TEXT}\nmember: {get_formatted_name(target_member)}')


@router.message(Command(cl.sett.name))
async def sett(message: Message):
    cpr = await CommandParser(message, cog.tickets(Real, creator_required=True)).parse()

    if not cpr.valid:
        return await _reply_by_crv(message, cpr)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    await service.sett(
        member=target_member,
        tickets=cpr.args[glob.TICKETS_ARG],
        description=cpr.args.get(glob.DESCRIPTION_ARG, None)
    )

    await message.answer(f'{glob.SETT_TEXT}\nmember: {get_formatted_name(target_member)}')


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
    answer = glob.MEMBER_FIRED if fired else glob.MEMBER_ALREADY_FIRED
    await message.answer(answer)


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
        CommandOverload(reply=True),
        CommandOverload().add(glob.USERNAME_ARG, Username),
        CommandOverload().add(glob.USER_ID_ARG, UserID)
    ], creator=True)

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await _reply_by_crv(message, cpr)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    if target_member.user_id == glob.CREATOR_USER_ID:
        return await message.answer(glob.UNREG_CREATOR_ERROR)

    await service.unreg(target_member)
    await message.answer(f'{glob.UNREG_TEXT}\nmember: {get_formatted_name(target_member)}')


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
