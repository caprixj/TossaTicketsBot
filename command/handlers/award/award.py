from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from command.util.crv import reply_by_crv
from command.util.validations import validate_message
from component.keyboards.keyboards import hide_keyboard
from model.database.awards import AwardMember
from model.types.custom.primitives import SID
from service import service_core as service
from command.parser.core import cog
from command.parser.core.parser import CommandParser
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(CL.award.name))
async def award(message: Message):
    if not await validate_message(message):
        return

    og = cog.a1_any(a1_name=glob.AWARD_ID_ARG, a1_type=SID, admin_required=True)
    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await reply_by_crv(message, cpr)

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
            reply_markup=await hide_keyboard(),
            parse_mode=ParseMode.HTML
        )
    else:
        await message.answer(glob.AWARD_DUPLICATE)
