from typing import Optional

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ForceReply

from command.routed.util.states import MsellStates
from model.database import Material
from service import service_core as service
import resources.glob as glob
from command.routed.handlers.public_handlers import tpay
from component.paged_viewer.paged_viewer import pmove, phide
from model.dto.transaction_dto import TransactionResultDTO
from command.routed.callbacks.custom_callback_data import get_operation_callback_data, get_msell_callback_data

router = Router()


""" Paged Viewer """


@router.callback_query(F.data.startswith(glob.PV_BACK_CALLBACK))
async def pv_back(callback: CallbackQuery):
    await pmove(callback, glob.PV_BACK_CALLBACK)


@router.callback_query(F.data.startswith(glob.PV_FORWARD_CALLBACK))
async def pv_forward(callback: CallbackQuery):
    await pmove(callback, glob.PV_FORWARD_CALLBACK)


@router.callback_query(F.data.startswith(glob.PV_HIDE_CALLBACK))
async def pv_hide(callback: CallbackQuery):
    await phide(callback)


""" Hide Callbacks """


@router.callback_query(F.data.startswith(glob.HIDE_CALLBACK))
async def hide(callback: CallbackQuery):
    await callback.message.delete()


""" /tpay """


@router.callback_query(F.data.startswith(glob.TPAY_YES_CALLBACK))
async def tpay_yes(callback: CallbackQuery):
    data = await get_operation_callback_data(callback.data)

    if callback.from_user.id != data.sender_id:
        await callback.answer(glob.ALERT_CALLBACK_YES, show_alert=True)
        return

    tr_: Optional[TransactionResultDTO] = await service.operation_manager.run(data.operation_id)

    if tr_ is None:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(glob.SERVICE_OPERATION_NONE_RESULT)
        return

    if not tr_.valid:
        await callback.message.answer(tr_.message)
        await callback.message.delete()
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.reply(glob.TPAY_TEXT)
    await callback.answer()


@router.callback_query(F.data.startswith(glob.TPAY_NO_CALLBACK))
async def tpay_no(callback: CallbackQuery):
    data = await get_operation_callback_data(callback.data)

    if callback.from_user.id != data.sender_id:
        await callback.answer(glob.ALERT_CALLBACK_NO, show_alert=True)
        return

    await service.operation_manager.cancel(data.operation_id)
    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data.startswith(glob.TPAY_FEE_INCORPORATION_CALLBACK))
async def tpay_fi(callback: CallbackQuery):
    data = await get_operation_callback_data(callback.data)

    if callback.from_user.id != data.sender_id:
        await callback.answer(glob.ALERT_CALLBACK_ACTION, show_alert=True)
        return

    command_message = await service.operation_manager.get_command_message(data.operation_id)
    if command_message is None:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(glob.SERVICE_OPERATION_NONE_RESULT)
        return

    await service.operation_manager.cancel(data.operation_id)
    await callback.answer()
    await tpay(
        message=command_message,
        callback_message=callback.message,
        fee_incorporated=True
    )


""" /msell """


@router.callback_query(F.data.startswith(glob.MSELL_CHOOSE_MATERIAL_CALLBACK))
async def msell_choose_material(callback: CallbackQuery, state: FSMContext):
    data = await get_msell_callback_data(callback.data)
    material = Material(
        emoji=data.emoji,
        name=await service.get_formatted_material_name(
            await service.get_material_name(data.emoji)
        )
    )

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(
        f'{glob.MSELL_CHOSEN_MATERIAL_EMOJI}: *{material.name}{material.emoji} ({data.quantity})*'
    )
    quantity_message = await callback.message.answer(
        text=f'{glob.MSELL_ASK_QUANTITY}',
        reply_markup=ForceReply(
            input_field_placeholder=glob.MSELL_FIELD_PLACEHOLDER,
            selective=True
        )
    )

    await state.update_data(
        user_id=data.sender_id,
        material=material,
        quantity_message_id=quantity_message.message_id
    )
    await state.set_state(MsellStates.waiting_for_quantity)

    await callback.answer()


@router.callback_query(StateFilter(MsellStates.waiting_for_confirmation), F.data.startswith(glob.MSELL_YES_CALLBACK))
async def msell_yes(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    user_id: int = data['user_id']
    quantity: int = data['quantity']
    revenue: int = data['revenue']
    single_tax: int = data['single_tax']
    msell_tax: int = data['msell_tax']

    sold_items_count_today = await service.get_sold_mc_today(user_id)

    if sold_items_count_today + quantity > glob.MSELL_ITEMS_LIMIT:
        await callback.message.answer(glob.MSELL_ITEMS_LIMIT_REACHED)
        await callback.answer()
        await state.clear()
        return

    member = await service.get_member(user_id)
    if member.tpay_available == 0:
        await callback.message.answer(glob.TPAY_UNAVAILABLE_ERROR)
        await callback.answer()
        await state.clear()
        return

    await service.msell_txn(data)

    await callback.message.edit_text(f'*{glob.MSELL_YES} {(revenue - single_tax - msell_tax) / 100:.2f} tc*')
    await callback.answer()
    await state.clear()


@router.callback_query(StateFilter(MsellStates.waiting_for_confirmation), F.data.startswith(glob.MSELL_NO_CALLBACK))
async def msell_no(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(glob.MSELL_NO)
    await callback.answer()
    await state.clear()


""" /tbox """


@router.callback_query(F.data.startswith(glob.TBOX_CALLBACK))
async def tbox_open(callback: CallbackQuery):
    data = await get_operation_callback_data(callback.data)

    if callback.from_user.id != data.sender_id:
        await callback.answer(glob.ALERT_CALLBACK_ACTION, show_alert=True)
        return

    response = await service.tbox(data.sender_id)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(response)
    await callback.answer()


""" Other """


@router.callback_query(F.data.startswith(glob.DECORATIVE_KEYBOARD_BUTTON))
async def decorative_keyboard_button(callback: CallbackQuery):
    await callback.answer()
