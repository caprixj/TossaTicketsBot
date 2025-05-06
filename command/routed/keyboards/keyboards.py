from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import resources.const.glob as glob
from command.routed.callbacks.callback_data import generate_callback_data


def tpay_keyboard(operation_id: int, sender_id: int, fee_incorporated: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    cd_yes = generate_callback_data(glob.TPAY_YES_CALLBACK, operation_id, sender_id)
    builder.row(InlineKeyboardButton(text=glob.CONTINUE_BTN, callback_data=cd_yes))

    cd_no = generate_callback_data(glob.TPAY_NO_CALLBACK, operation_id, sender_id)
    builder.row(InlineKeyboardButton(text=glob.CANCEL_BTN, callback_data=cd_no))

    if fee_incorporated:
        cd_fi = generate_callback_data(glob.TPAY_FEE_INCORPORATION_CALLBACK, operation_id, sender_id)
        builder.row(InlineKeyboardButton(text=glob.INCORPORATE_FEE_BTN, callback_data=cd_fi))

    return builder.as_markup()


def hide_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=glob.HIDE_BTN, callback_data=callback_data))
    return builder.as_markup()


# def bhf_keyboard() -> InlineKeyboardMarkup:
#     builder = InlineKeyboardBuilder()
#     builder.row(InlineKeyboardButton(
#         text=glob.CLAIM_BTN,
#         callback_data=glob.CLAIM_BHF_CALLBACK
#     ))
#     return builder.as_markup()
