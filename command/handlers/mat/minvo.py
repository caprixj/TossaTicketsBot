from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import resources.glob as glob
from component.keyboards.keyboards import hide_keyboard, abort_keyboard
from model.database.materials import MaterialOrder
from model.types.custom.primitives import OrderCode
from model.types.enums import MaterialDealStatus
from service import service_core as service
from command.util.validations import validate_message
from command.parser.core import cog
from command.parser.core.parser import CommandParser
from command.parser.types.command_list import CommandList as CL
from service.cbdata.encoding import ldecode_cbdata
from utils import funcs
from utils.funcs import get_formatted_name

router = Router()


@router.message(Command(CL.minvo.name))
async def minvo(message: Message):
    if not await validate_message(message):
        return

    cpr = await CommandParser(
        message=message,
        overload_group=cog.le_id_any(
            id_name=glob.ORDER_CODE_ARG,
            id_type=OrderCode
        )
    ).parse()

    if not cpr.valid:
        return await message.answer(glob.COM_PARSER_FAILED)

    async def list_handler():
        target_member = await service.get_target_member(cpr)
        if target_member is None:
            return await message.answer(glob.GET_MEMBER_FAILED)

        minvos = await service.get_minvos_page(target_member.user_id)
        name_ping = get_formatted_name(
            member=await service.get_member(target_member.user_id),
            ping=True
        )

        await message.answer(
            text=f'{glob.MINVO_TITLE}'
                 f'\n{glob.MINVO_MEMBER}: {name_ping}'
                 f'\n\n{minvos}',
            reply_markup=await hide_keyboard(sender_lock=message.from_user.id)
        )

    async def admin_element():
        order: MaterialOrder = await service.get_material_order(
            order_code=cpr.args[glob.ORDER_CODE_ARG]
        )

        if not order:
            return await message.answer(glob.ORDER_NOT_FOUND)

        await message.answer(
            text=await service.get_minvo_details(order),
            reply_markup=await hide_keyboard(sender_lock=message.from_user.id)
        )

    async def user_element():
        order: MaterialOrder = await service.get_material_order(
            order_code=cpr.args[glob.ORDER_CODE_ARG]
        )

        if not order:
            return await message.answer(glob.ORDER_NOT_FOUND)

        if message.from_user.id != order.sender_id:
            return await message.answer(glob.ORDER_FORBIDDEN)

        await message.answer(
            text=await service.get_minvo_details(order),
            reply_markup=abort_keyboard(
                order_code=order.code,
                sender_lock=message.from_user.id
            )
        )

    if cpr.overload.otype == 'list':
        await list_handler()
    elif cpr.overload.admin:
        await admin_element()
    else:
        await user_element()


@router.callback_query(F.data.contains(glob.MINVO_ABORT))
async def abort(callback: CallbackQuery, bot: Bot):
    order_code, sender_lock = ldecode_cbdata(callback.data, [str, int])
    order = await service.get_material_order(order_code)

    if not order:
        await callback.message.edit_reply_markup(reply_markup=None)
        await funcs.callback_struck_html(callback)
        return await callback.message.reply(glob.ORDER_NOT_FOUND)

    if sender_lock != callback.from_user.id:
        return await callback.answer(glob.ALERT_CALLBACK_ACTION, show_alert=True)

    await service.cancel_material_deal(order_code, status=MaterialDealStatus.ABORTED)

    await callback.message.edit_reply_markup(reply_markup=None)
    await funcs.callback_struck_html(callback)

    try:
        await bot.send_message(
            chat_id=order.receiver_id,
            text=f'{glob.MINVO_ABORTED} (#{order_code})'
        )
        notified = True
    except (TelegramForbiddenError, TelegramBadRequest):
        notified = False

    await callback.message.reply(
        f'*{glob.MINVO_ABORTED}*'
        f'\n\n{glob.MSEND_SENDER_NOTIFIED_SUCCESS if notified else glob.MSEND_SENDER_NOTIFIED_FAILED}'
    )
