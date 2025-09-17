import functools
from typing import Optional
from uuid import UUID

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import resources.glob as glob
from model.dto.txn_dto import TransactionResultDTO
from model.types.custom.primitives import PNRealTickets
from service import service_core as service
from command.util.validations import validate_message
from component.keyboards.keyboards import tpay_keyboard
from command.parser.core import cog
from command.parser.core.parser import CommandParser
from command.parser.types.command_list import CommandList as CL
from service.cbdata.encoding import ldecode_cbdata
from utils import funcs

router = Router()


@router.message(Command(CL.tpay.name))
async def tpay(message: Message, callback_message: Message = None, fee_incorporated: bool = False):
    if not await validate_message(message):
        return

    cpr = await CommandParser(message, cog.tickets(PNRealTickets, admin_required=False)).parse()

    if not cpr.valid:
        return await message.answer(glob.COM_PARSER_FAILED)

    receiver = await service.get_target_member(cpr)

    if receiver is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    sender = await service.get_member(message.from_user.id)

    if sender.tpay_available == 0:
        return await message.answer(glob.TPAY_UNAVAILABLE_ERROR)

    if sender.user_id == receiver.user_id:
        return await message.answer(glob.SELF_TRANS_ERROR)

    description = cpr.args.get(glob.DESCRIPTION_ARG, None)

    # t - total, x - transfer, f - fee
    # -> (t, x, f)
    async def calculate_transfer(x: int) -> (int, int, int):
        if fee_incorporated:
            t_fi = x
            x_fi = await funcs.get_transfer_by_total(t_fi)
            return t_fi, x_fi, t_fi - x_fi
        else:
            f = await funcs.get_single_tax(x)
            return x + f, x, f

    total, transfer, fee = await calculate_transfer(cpr.args[glob.TICKETS_ARG])

    tpay_text = (f'{glob.TPAY_SENDER}: {funcs.get_formatted_name(sender, ping=True)}'
                 f'\n{glob.TPAY_RECEIVER}: {funcs.get_formatted_name(receiver, ping=True)}'
                 f'\n\n*{glob.TPAY_TOTAL}: {total / 100:.2f}*'
                 f'\n{glob.AMOUNT_RES}: {transfer / 100:.2f}'
                 f'\n{glob.TPAY_TAX}: {fee / 100:.2f} '
                 f'({int(100 * glob.SINGLE_TAX)}%, min {glob.MIN_SINGLE_TAX / 100:.2f})'
                 f'\n\n{glob.TPAY_DESCRIPTION}: _{description}_')

    operation_id = await service.som().reg(
        func=functools.partial(service.tpay, sender, receiver, transfer, description),
        data={'command_message': message}
    )

    if fee_incorporated:
        await callback_message.edit_text(text=tpay_text)
        await callback_message.edit_reply_markup(
            reply_markup=await tpay_keyboard(
                operation_id=operation_id,
                sender_id=sender.user_id,
                fee_incorporated=False
            )
        )
    else:
        await message.answer(
            text=tpay_text,
            reply_markup=await tpay_keyboard(
                operation_id=operation_id,
                sender_id=sender.user_id,
                fee_incorporated=transfer > glob.MIN_SINGLE_TAX
            )
        )


@router.callback_query(F.data.contains(glob.TPAY_YES_CALLBACK))
async def tpay_yes(callback: CallbackQuery):
    sender_id, operation_id = ldecode_cbdata(
        data=callback.data,
        binding_types=[int, UUID]
    )

    if callback.from_user.id != sender_id:
        await callback.answer(glob.ALERT_CALLBACK_YES, show_alert=True)
        return

    tr_: Optional[TransactionResultDTO] = await service.som().run(operation_id)

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


@router.callback_query(F.data.contains(glob.TPAY_NO_CALLBACK))
async def tpay_no(callback: CallbackQuery):
    sender_id, operation_id = ldecode_cbdata(
        data=callback.data,
        binding_types=[int, UUID]
    )

    if callback.from_user.id != sender_id:
        await callback.answer(glob.ALERT_CALLBACK_NO, show_alert=True)
        return

    await service.som().cancel(operation_id)
    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data.contains(glob.TPAY_FEE_INCORPORATION_CALLBACK))
async def tpay_fi(callback: CallbackQuery):
    sender_id, operation_id = ldecode_cbdata(
        data=callback.data,
        binding_types=[int, UUID]
    )

    if callback.from_user.id != sender_id:
        await callback.answer(glob.ALERT_CALLBACK_ACTION, show_alert=True)
        return

    opdata = await service.som().get_data(operation_id)
    if not opdata:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.edit_text(
            text=funcs.struck_html(callback.message.text),
            parse_mode=ParseMode.HTML,
        )
        await callback.answer(glob.CALLBACK_EXPIRED, show_alert=True)
        return

    com_msg = opdata['command_message']
    if com_msg is None:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(glob.SERVICE_OPERATION_NONE_RESULT)
        return

    await service.som().cancel(operation_id)
    await callback.answer()
    await tpay(
        message=com_msg,
        callback_message=callback.message,
        fee_incorporated=True
    )
