from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import resources.const.glob as glob
from command.routed.callbacks.custom_callback_data import OperationCallbackData, MsellCallbackData


def tpay_keyboard(operation_id: int, sender_id: int, fee_incorporated: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    cd_yes = OperationCallbackData(glob.TPAY_YES_CALLBACK, sender_id, operation_id)
    builder.row(InlineKeyboardButton(text=glob.CONTINUE_BTN, callback_data=cd_yes.tostr()))

    cd_no = OperationCallbackData(glob.TPAY_NO_CALLBACK, sender_id, operation_id)
    builder.row(InlineKeyboardButton(text=glob.CANCEL_BTN, callback_data=cd_no.tostr()))

    if fee_incorporated:
        cd_fi = OperationCallbackData(glob.TPAY_FEE_INCORPORATION_CALLBACK, sender_id, operation_id)
        builder.row(InlineKeyboardButton(text=glob.INCORPORATE_FEE_BTN, callback_data=cd_fi.tostr()))

    return builder.as_markup()


def msell_choose_material_keyboard(keyboard_data: list[list[str]], sender_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for row in keyboard_data:
        keyboard_row = list()
        for btn in row:
            mcd = MsellCallbackData(
                callback_name=glob.MSELL_CHOOSE_MATERIAL_CALLBACK,
                sender_id=sender_id,
                emoji=btn.split()[0],
                quantity=int(btn.split()[1])
            )
            keyboard_row.append(InlineKeyboardButton(text=btn, callback_data=mcd.tostr()))
        builder.row(*keyboard_row)

    return builder.as_markup()


def msell_confirmation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=glob.CONTINUE_BTN, callback_data=glob.MSELL_YES_CALLBACK))
    builder.row(InlineKeyboardButton(text=glob.CANCEL_BTN, callback_data=glob.MSELL_NO_CALLBACK))

    return builder.as_markup()


def hide_keyboard() -> InlineKeyboardMarkup:
    return one_btn_keyboard(glob.HIDE_BTN, glob.HIDE_CALLBACK)


def one_btn_keyboard(text: str, callback_name: str, sender_id: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    callback_data = OperationCallbackData(callback_name=callback_name, sender_id=sender_id)
    builder.row(InlineKeyboardButton(text=text, callback_data=callback_data.tostr()))

    return builder.as_markup()
