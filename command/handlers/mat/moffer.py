from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from component.keyboards.keyboards import hide_keyboard, order_accept_keyboard
from model.database.materials import MaterialOrder
from model.types.custom.primitives import OrderCode
from service import service_core as service
from command.util.validations import validate_message
from command.parser.core import cog
from command.parser.core.parser import CommandParser
from command.parser.types.command_list import CommandList as CL
from utils.funcs import get_formatted_name

router = Router()


@router.message(Command(CL.moffer.name))
async def moffer(message: Message):
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

        moffers = await service.get_moffers_page(target_member.user_id)
        name_ping = get_formatted_name(
            member=await service.get_member(target_member.user_id),
            ping=True
        )

        await message.answer(
            text=f'{glob.MOFFER_TITLE}'
                 f'\n{glob.MOFFER_MEMBER}: {name_ping}'
                 f'\n\n{moffers}',
            reply_markup=await hide_keyboard(sender_lock=message.from_user.id)
        )

    async def admin_element():
        order: MaterialOrder = await service.get_material_order(
            order_code=cpr.args[glob.ORDER_CODE_ARG]
        )

        if not order:
            return await message.answer(glob.ORDER_NOT_FOUND)

        await message.answer(
            text=await service.get_moffer_details(order),
            reply_markup=order_accept_keyboard(
                order_code=order.code,
                receiver_lock=order.receiver_id
            )
        )

    async def user_element():
        order: MaterialOrder = await service.get_material_order(
            order_code=cpr.args[glob.ORDER_CODE_ARG]
        )

        if not order:
            return await message.answer(glob.ORDER_NOT_FOUND)

        if message.from_user.id == order.sender_id:
            return await message.answer(glob.USE_MINVO_INSTEAD)

        if message.from_user.id != order.receiver_id:
            return await message.answer(glob.ORDER_FORBIDDEN)

        await message.answer(
            text=await service.get_moffer_details(order),
            reply_markup=order_accept_keyboard(
                order_code=order.code,
                receiver_lock=order.receiver_id
            )
        )

    if cpr.overload.otype == 'list':
        await list_handler()
    elif cpr.overload.admin:
        await admin_element()
    else:
        await user_element()
