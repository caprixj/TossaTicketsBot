from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import resources.const.glob as glob
from command.routed.callbacks.custom_callback_data import CustomCallbackData


def tpay_keyboard(operation_id: int, sender_id: int, fee_incorporated: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    cd_yes = CustomCallbackData(glob.TPAY_YES_CALLBACK, sender_id, operation_id)
    builder.row(InlineKeyboardButton(text=glob.CONTINUE_BTN, callback_data=cd_yes.tostr()))

    cd_no = CustomCallbackData(glob.TPAY_NO_CALLBACK, sender_id, operation_id)
    builder.row(InlineKeyboardButton(text=glob.CANCEL_BTN, callback_data=cd_no.tostr()))

    if fee_incorporated:
        cd_fi = CustomCallbackData(glob.TPAY_FEE_INCORPORATION_CALLBACK, sender_id, operation_id)
        builder.row(InlineKeyboardButton(text=glob.INCORPORATE_FEE_BTN, callback_data=cd_fi.tostr()))

    return builder.as_markup()


def hide_keyboard(callback_name: str) -> InlineKeyboardMarkup:
    return one_btn_keyboard(glob.HIDE_BTN, callback_name)


def one_btn_keyboard(text: str, callback_name: str, sender_id: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    callback_data = CustomCallbackData(callback_name=callback_name, sender_id=sender_id)
    builder.row(InlineKeyboardButton(text=text, callback_data=callback_data.tostr()))

    return builder.as_markup()
