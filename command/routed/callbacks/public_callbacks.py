from typing import Optional

from aiogram import Router
from aiogram.types import CallbackQuery

from service import service_core as service
import resources.const.glob as glob
from command.routed.handlers.public_handlers import tpay
from component.paged_viewer.paged_viewer import pmove, phide
from model.results.transaction_result import TransactionResult
from command.routed.callbacks.callback_data import get_callback_data

router = Router()


@router.callback_query(lambda c: c.data.startswith(glob.DECORATIVE_KEYBOARD_BUTTON))
async def decorative_keyboard_button(callback: CallbackQuery):
    await callback.answer()


""" paged viewer """


@router.callback_query(lambda c: c.data.startswith(glob.PV_BACK_CALLBACK))
async def pv_back(callback: CallbackQuery):
    await pmove(callback, glob.PV_BACK_CALLBACK)


@router.callback_query(lambda c: c.data.startswith(glob.PV_FORWARD_CALLBACK))
async def pv_forward(callback: CallbackQuery):
    await pmove(callback, glob.PV_FORWARD_CALLBACK)


@router.callback_query(lambda c: c.data.startswith(glob.PV_HIDE_CALLBACK))
async def pv_hide(callback: CallbackQuery):
    await phide(callback)


""" hide callbacks """


@router.callback_query(lambda c: c.data.startswith(glob.HELP_HIDE_CALLBACK))
async def help_hide(callback: CallbackQuery):
    await callback.message.delete()


@router.callback_query(lambda c: c.data.startswith(glob.AWARD_HIDE_CALLBACK))
async def award_hide(callback: CallbackQuery):
    await callback.message.delete()


@router.callback_query(lambda c: c.data.startswith(glob.TOPT_HIDE_CALLBACK))
async def topt_hide(callback: CallbackQuery):
    await callback.message.delete()


""" /tpay """


@router.callback_query(lambda c: c.data.startswith(glob.TPAY_YES_CALLBACK))
async def tpay_yes(callback: CallbackQuery):
    data = await get_callback_data(callback.data)

    if callback.from_user.id != data.sender_id:
        await callback.answer(glob.ALERT_CALLBACK_YES, show_alert=True)
        return

    tr_: Optional[TransactionResult] = await service.operation_manager.run(data.operation_id)

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


@router.callback_query(lambda c: c.data.startswith(glob.TPAY_NO_CALLBACK))
async def tpay_no(callback: CallbackQuery):
    data = await get_callback_data(callback.data)

    if callback.from_user.id != data.sender_id:
        await callback.answer(glob.ALERT_CALLBACK_NO, show_alert=True)
        return

    await service.operation_manager.cancel(data.operation_id)
    await callback.message.delete()
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith(glob.TPAY_FEE_INCORPORATION_CALLBACK))
async def tpay_fi(callback: CallbackQuery):
    data = await get_callback_data(callback.data)

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
