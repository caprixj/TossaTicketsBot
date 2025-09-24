from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State

import resources.glob as glob
from model.types.custom.primitives import PNRealTickets, PNInt, Username, UserID, Text256
from model.types.enums import MaterialDealResult, MaterialDealStatus
from service import service_core as service
from command.util.validations import validate_message
from component.keyboards.keyboards import choose_material_keyboard, msend_see_details_keyboard, order_accept_keyboard
from component.keyboards.keyboards import confirmation_keyboard
from command.parser.core import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from command.parser.types.command_list import CommandList as CL
from model.database.materials import Material, Ingredient, MaterialOrder
from service.cbdata.encoding import ldecode_cbdata, encode_cbdata
from service.cbdata.redis_stash import peek_payload
from utils import funcs
from utils.funcs import get_formatted_name


class MsendStates(StatesGroup):
    waiting_for_material = State()
    waiting_for_quantity = State()
    waiting_for_transfer = State()
    waiting_for_confirmation = State()


router = Router()


@router.message(Command(CL.msend.name))
async def msend(message: Message):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
            CommandOverload().add(glob.USERNAME_ARG, Username),
            CommandOverload().add(glob.USERNAME_ARG, Username).add(glob.DESCRIPTION_ARG, Text256),
            CommandOverload().add(glob.USER_ID_ARG, UserID),
            CommandOverload().add(glob.USER_ID_ARG, UserID).add(glob.DESCRIPTION_ARG, Text256)
        ], private=True
    )

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        if cpr.private_violation:
            await message.answer(glob.PRIVATE_VIOLATION)
        else:
            await message.answer(glob.COM_PARSER_FAILED)
        return

    receiver = await service.get_target_member(cpr)

    if receiver is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    sender = await service.get_member(message.from_user.id)

    if sender.user_id == receiver.user_id:
        return await message.answer(glob.SELF_MSEND_ERROR)

    keyboard_data = await service.get_materials_markup(message.from_user.id)

    await message.reply(
        text=glob.MSEND_TEXT,
        reply_markup=await choose_material_keyboard(
            keyboard_data=keyboard_data,
            signature=glob.MSEND_QUANTITY_CALLBACK,
            user_id=sender.user_id,
            target_id=receiver.user_id,
            description=cpr.args.get(glob.DESCRIPTION_ARG, None)
        )
    )


@router.callback_query(F.data.contains(glob.MSEND_QUANTITY_CALLBACK))
async def msend_quantity(callback: CallbackQuery, state: FSMContext):
    # (redis) get button's data
    data = await peek_payload(callback)
    if not data:
        return await callback.answer(glob.FLOW_EXPIRED, show_alert=True)

    # (core) process data
    emoji: str = data['emoji']
    quantity: int = data['quantity']
    reserved: int = data['reserved']
    sender_id: int = data['user_id']
    receiver_id: int = data['target_id']
    description: str = data['description']
    material = Material(
        emoji=emoji,
        name=await service.get_formatted_material_name(
            await service.get_material_name(emoji)
        )
    )

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(
        f"{glob.MSEND_CHOSEN_MATERIAL_EMOJI}: *{material.name}{material.emoji} ({quantity - reserved})*"
    )
    await callback.message.answer(glob.MSEND_ASK_QUANTITY)

    # (fsm) pass flow's data and set the state
    await state.update_data(
        sender_id=sender_id,
        receiver_id=receiver_id,
        material=material,
        reserved=reserved,
        description=description
    )
    await state.set_state(MsendStates.waiting_for_quantity)

    await callback.answer()


@router.message(StateFilter(MsendStates.waiting_for_quantity))
async def msend_transfer(message: Message, state: FSMContext):
    # (fsm) get flow's data
    data = await state.get_data()
    if not data:
        await state.clear()
        return await message.answer(glob.FLOW_EXPIRED, show_alert=True)

    # (core) process data
    if not PNInt(message.text).validate():
        return await message.answer(glob.MSEND_QUANTITY_INVALID)

    quantity = int(message.text)
    material_bal: Ingredient = await service.get_member_material(
        user_id=data['sender_id'],
        material_name=data['material'].name
    )

    available = material_bal.quantity - data['reserved']
    if material_bal is None or available < quantity:
        return await message.answer(glob.MSEND_QUANTITY_INSUFFICIENT)

    # (fsm) pass flow's data and set the state
    await state.update_data(quantity=quantity)
    await state.set_state(MsendStates.waiting_for_transfer)

    await message.answer(glob.MSEND_ASK_TRANSFER)


@router.message(StateFilter(MsendStates.waiting_for_transfer))
async def msend_confirm(message: Message, state: FSMContext):
    # (fsm) get flow's data
    data = await state.get_data()
    if not data:
        await state.clear()
        return await message.answer(glob.FLOW_EXPIRED, show_alert=True)

    # (core) process data
    t_model = PNRealTickets(message.text)
    if not t_model.validate():
        return await message.answer(glob.MSEND_QUANTITY_INVALID)

    transfer: int = await t_model.cast()
    material: Material = data['material']
    to_sell: int = data['quantity']
    description: str = data['description']
    material_name: str = data['material'].name

    sender = await service.get_member(data['sender_id'])
    receiver = await service.get_member(data['receiver_id'])

    if not sender:
        await state.clear()
        return await message.answer(glob.SENDER_NO_LONGER_EXISTS)

    if not receiver:
        await state.clear()
        return await message.answer(glob.RECEIVER_NO_LONGER_EXISTS)

    details = await service.calculate_material_order_cost_details(material_name, to_sell, transfer)

    # (fsm) pass flow's data and set the state
    await state.update_data(
        mat_sender_id=sender.user_id,
        mat_receiver_id=receiver.user_id,
        quantity=to_sell,
        rate_price=details.rate_price,
        rate_cost=details.rate_cost,
        offered_price=details.offered_price,
        offered_cost=transfer,
        single_tax=details.single_tax,
        msend_tax=details.msend_tax,
        total_cost=details.total_cost,
        description=description,
        material_name=material_name
    )
    await state.set_state(MsendStates.waiting_for_confirmation)

    # (core) send a confirmation form
    await message.answer(
        text=(f'*{glob.MSEND_MAT_ORDER}*'
              f'\n\n{glob.MSEND_SENDER}: {get_formatted_name(sender, ping=True)}'
              f'\n{glob.MSEND_RECEIVER}: {get_formatted_name(receiver, ping=True)}'
              f'\n\n{glob.MSEND_YOU_SEND}: *{to_sell} {material.name}{material.emoji}*'
              f'\n{glob.MSEND_YOU_RECEIVE}: *{transfer / 100:.2f} tc*'
              f'\n\n{glob.MSEND_BUYER_PAYS}: {details.total_cost / 100:.2f} tc'
              f'\n\n{glob.MSEND_SINGLE_TAX_TEXT}: {details.single_tax / 100:.2f} tc ({int(glob.SINGLE_TAX * 100)}%)'
              f'\n{glob.MSEND_MSEND_TAX_TEXT}: {details.msend_tax / 100:.2f} tc ({int(glob.MSEND_TAX * 100)}%)'
              f'\n\n{glob.MSEND_RATE_PRICE}: {details.rate_price / 100:.7f} tc'
              f'\n{glob.MSEND_YOUR_PRICE}: {details.offered_price / 100:.7f} tc'
              f'\n\n{glob.MSEND_DESCRIPTION}: _{description}_'),
        reply_markup=confirmation_keyboard(
            yes_cbdata=glob.MSEND_YES_CALLBACK,
            no_cbdata=glob.MSEND_NO_CALLBACK
        )
    )


@router.callback_query(StateFilter(MsendStates.waiting_for_confirmation), F.data.contains(glob.MSEND_YES_CALLBACK))
async def msend_yes(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.edit_reply_markup(reply_markup=None)

    # (fsm) get flow's data
    data = await state.get_data()
    if not data:
        return await callback.answer(glob.FLOW_EXPIRED, show_alert=True)

    # (core) process data
    order = await service.msend_reserve(data)
    if not order:
        return await callback.message.answer(glob.MSEND_QUANTITY_INSUFFICIENT)

    # notify the receiver about the incoming trade offer
    try:
        await bot.send_message(
            chat_id=data['mat_receiver_id'],
            text=glob.MSEND_RECEIVER_NOTIFICATION,
            reply_markup=msend_see_details_keyboard(order.code)
        )
        notified = True
    except (TelegramForbiddenError, TelegramBadRequest):
        notified = False

    await state.clear()
    await callback.message.answer(
        text=f'<b>{glob.MSEND_YES}</b> #{order.code}'
             f'\n{glob.MSEND_CODE}: <code>{order.code}</code> {glob.MSEND_COPY}'
             f'\n\n{glob.MSEND_RECEIVER_NOTIFIED_SUCCESS if notified else glob.MSEND_RECEIVER_NOTIFIED_FAILED}'
             f'\n\n<blockquote>{glob.MSEND_YES_HINT}</blockquote>',
        parse_mode=ParseMode.HTML
    )


@router.callback_query(StateFilter(MsendStates.waiting_for_confirmation), F.data.contains(glob.MSEND_NO_CALLBACK))
async def msend_no(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(glob.MSEND_NO)
    await callback.answer()
    await state.clear()


@router.callback_query(F.data.contains(glob.ORDER_SEE_DETAILS_CALLBACK))
async def see_details(callback: CallbackQuery):
    code, = ldecode_cbdata(callback.data)
    order: MaterialOrder = await service.get_material_order(code)

    if not order:
        await callback.message.edit_reply_markup(reply_markup=None)
        return await callback.answer(glob.ORDER_NOT_FOUND, show_alert=True)

    sender = await service.get_member(order.sender_id)
    if not sender:
        await callback.message.edit_reply_markup(reply_markup=None)
        return await callback.answer(glob.SENDER_NO_LONGER_EXISTS, show_alert=True)

    receiver = await service.get_member(order.receiver_id)
    if not receiver:
        await callback.message.edit_reply_markup(reply_markup=None)
        return await callback.answer(glob.RECEIVER_NO_LONGER_EXISTS, show_alert=True)

    await callback.message.edit_text(
        text=await service.get_moffer_details(order),
        reply_markup=order_accept_keyboard(
            order_code=order.code,
            receiver_lock=receiver.user_id
        )
    )


@router.callback_query(F.data.contains(glob.ORDER_ACCEPT_CALLBACK))
async def accept_material_deal(callback: CallbackQuery):
    order_code, receiver_lock = ldecode_cbdata(callback.data, [str, int])

    if receiver_lock != callback.from_user.id:
        return await callback.answer(glob.ALERT_CALLBACK_ACTION, show_alert=True)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.reply(
        text=glob.MSEND_ACCEPT_CONFIRM,
        reply_markup=confirmation_keyboard(
            yes_cbdata=encode_cbdata(
                signature=glob.ORDER_ACCEPT_YES_CALLBACK,
                data={'code': order_code}
            ),
            no_cbdata=encode_cbdata(
                signature=glob.ORDER_ACCEPT_NO_CALLBACK,
                data={'code': order_code}
            ),
        )
    )


@router.callback_query(F.data.contains(glob.ORDER_ACCEPT_YES_CALLBACK))
async def accept_material_deal_yes(callback: CallbackQuery, bot: Bot):
    await callback.message.edit_reply_markup(reply_markup=None)

    order_code, = ldecode_cbdata(callback.data)
    order: MaterialOrder = await service.get_material_order(order_code)
    result = await service.accept_trade_deal(order)

    if result != MaterialDealResult.SUCCESS:
        if result == MaterialDealResult.SENDER_NOT_FOUND:
            return await callback.answer(glob.SENDER_NOT_FOUND, show_alert=True)
        elif result == MaterialDealResult.RECEIVER_NOT_FOUND:
            return await callback.answer(glob.RECEIVER_NOT_FOUND, show_alert=True)
        elif result == MaterialDealResult.MATERIAL_NOT_FOUND:
            return await callback.answer(glob.MATERIAL_NOT_FOUND, show_alert=True)
        elif result == MaterialDealResult.NOT_ENOUGH_MATERIAL:
            return await callback.answer(glob.NOT_ENOUGH_MATERIAL, show_alert=True)
        elif result == MaterialDealResult.RESERVATION_VIOLATED:
            return await callback.answer(glob.RESERVATION_VIOLATED, show_alert=True)
        elif result == MaterialDealResult.INSUFFICIENT_FUNDS:
            return await callback.answer(glob.INSUFFICIENT_FUNDS, show_alert=True)
        else:
            return await callback.answer(glob.UNKNOWN_ENUM, show_alert=True)

    try:
        await bot.send_message(
            chat_id=order.sender_id,
            text=f'{glob.MSEND_ACCEPTED} (#{order.code})'
        )
        notified = True
    except (TelegramForbiddenError, TelegramBadRequest):
        notified = False

    await callback.message.reply(
        f'*{glob.MSEND_ACCEPTED}*'
        f'\n\n{glob.MSEND_SENDER_NOTIFIED_SUCCESS if notified else glob.MSEND_SENDER_NOTIFIED_FAILED}'
    )


@router.callback_query(F.data.contains(glob.ORDER_ACCEPT_NO_CALLBACK))
async def accept_material_deal_no(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.reply(glob.MSEND_ACCEPT_NO)


@router.callback_query(F.data.contains(glob.ORDER_REJECT_CALLBACK))
async def reject_material_deal(callback: CallbackQuery, bot: Bot):
    order_code, receiver_lock = ldecode_cbdata(callback.data, [str, int])
    order = await service.get_material_order(order_code)

    if not order:
        await funcs.callback_struck_html(callback)
        await callback.message.edit_reply_markup(reply_markup=None)
        return await callback.message.reply(glob.ORDER_NOT_FOUND)

    if receiver_lock != callback.from_user.id:
        return await callback.answer(glob.ALERT_CALLBACK_ACTION, show_alert=True)

    await service.cancel_material_deal(order_code, status=MaterialDealStatus.REJECTED)

    await callback.message.edit_reply_markup(reply_markup=None)
    await funcs.callback_struck_html(callback)

    try:
        await bot.send_message(
            chat_id=order.sender_id,
            text=f'{glob.MSEND_REJECTED} (#{order_code})'
        )
        notified = True
    except (TelegramForbiddenError, TelegramBadRequest):
        notified = False

    await callback.message.reply(
        f'*{glob.MSEND_REJECTED}*'
        f'\n\n{glob.MSEND_SENDER_NOTIFIED_SUCCESS if notified else glob.MSEND_SENDER_NOTIFIED_FAILED}'
    )
