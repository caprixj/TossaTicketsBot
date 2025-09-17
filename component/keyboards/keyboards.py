import asyncio
import re
from uuid import UUID

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import resources.glob as glob
from service.cbdata.encoding import encode_cbkey, encode_cbdata
from service.cbdata.redis_stash import stash_payload


async def tpay_keyboard(operation_id: UUID, sender_id: int, fee_incorporated: bool) -> InlineKeyboardMarkup:
    async def _build_button(btn_text: str, callback_name: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=btn_text,
            callback_data=encode_cbdata(
                signature=callback_name,
                data={
                    'sender_id': sender_id,
                    'operation_id': operation_id
                }
            )
        )

    builder = InlineKeyboardBuilder()

    builder.row(await _build_button(
        btn_text=glob.CONTINUE_BTN,
        callback_name=glob.TPAY_YES_CALLBACK
    ))

    builder.row(await _build_button(
        btn_text=glob.CANCEL_BTN,
        callback_name=glob.TPAY_NO_CALLBACK
    ))

    if fee_incorporated:
        builder.row(await _build_button(
            btn_text=glob.INCORPORATE_FEE_BTN,
            callback_name=glob.TPAY_FEE_INCORPORATION_CALLBACK
        ))

    return builder.as_markup()


async def choose_material_keyboard(
        keyboard_data: list[list[str]], signature: str, user_id: int, target_id: int = 0, description: str = None
) -> InlineKeyboardMarkup:
    async def _build_button(btn_text: str) -> InlineKeyboardButton:
        # btn_text cases (examples):
        # 1) "◾️ 148 (-8)" - 3 splits
        # 2) "◾️ 148" - 2 splits
        split = btn_text.split(' ')
        emoji = split[0]
        quantity = int(split[1])
        reserved = int(re.sub(r'[-()]', '', split[2])) if len(split) == 3 else 0

        btn_key = await stash_payload({
            'user_id': user_id,
            'target_id': target_id,
            'emoji': emoji,
            'quantity': quantity,
            'reserved': reserved,
            'description': description
        })

        return InlineKeyboardButton(
            text=btn_text,
            callback_data=encode_cbkey(btn_key, signature)
        )

    builder = InlineKeyboardBuilder()

    for row in keyboard_data:
        builds = [_build_button(btn) for btn in row]
        buttons = await asyncio.gather(*builds)
        builder.row(*buttons)

    return builder.as_markup()


def confirmation_keyboard(yes_cbdata: str, no_cbdata: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=glob.CONTINUE_BTN, callback_data=yes_cbdata))
    builder.row(InlineKeyboardButton(text=glob.CANCEL_BTN, callback_data=no_cbdata))
    return builder.as_markup()


def abort_keyboard(order_code: str, sender_lock: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=glob.ABORT_BTN,
        callback_data=encode_cbdata(
            signature=glob.MINVO_ABORT,
            data={
                'order_code': order_code,
                'sender_lock': sender_lock
            }
        )
    ))
    builder.row(InlineKeyboardButton(
        text=glob.HIDE_BTN,
        callback_data=encode_cbdata(
            signature=glob.HIDE_CALLBACK,
            data={'sender_id': sender_lock}
        )
    ))

    return builder.as_markup()


def order_accept_keyboard(order_code: str, receiver_lock: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=glob.ACCEPT_BTN,
        callback_data=encode_cbdata(
            signature=glob.ORDER_ACCEPT_CALLBACK,
            data={
                'order_code': order_code,
                'receiver_lock': receiver_lock
            }
        )
    ))
    builder.row(InlineKeyboardButton(
        text=glob.REJECT_BTN,
        callback_data=encode_cbdata(
            signature=glob.ORDER_REJECT_CALLBACK,
            data={
                'order_code': order_code,
                'receiver_lock': receiver_lock
            }
        )
    ))
    builder.row(InlineKeyboardButton(
        text=glob.HIDE_BTN,
        callback_data=encode_cbdata(
            signature=glob.HIDE_CALLBACK,
            data={'sender_id': receiver_lock}
        )
    ))
    return builder.as_markup()


def msend_see_details_keyboard(order_code: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=glob.MSEND_SEE_DETAILS_BTN,
            callback_data=encode_cbdata(
                signature=glob.ORDER_SEE_DETAILS_CALLBACK,
                data={'code': order_code}
            )
        )
    )

    return builder.as_markup()


async def hide_keyboard(sender_lock: int = 0) -> InlineKeyboardMarkup:
    return await one_btn_keyboard(
        text=glob.HIDE_BTN,
        callback_name=glob.HIDE_CALLBACK,
        sender_lock=sender_lock
    )


async def one_btn_keyboard(text: str, callback_name: str, sender_lock: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=text,
        callback_data=encode_cbdata(
            signature=callback_name,
            data={'sender_id': sender_lock}
        )
    ))

    return builder.as_markup()
