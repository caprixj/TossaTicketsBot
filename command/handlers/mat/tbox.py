from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import resources.glob as glob
from service import service_core as service
from command.util.validations import validate_message
from component.keyboards.keyboards import one_btn_keyboard
from command.parser.types.command_list import CommandList as CL
from service.cbdata.encoding import ldecode_cbdata

router = Router()


@router.message(Command(CL.tbox.name))
async def tbox(message: Message):
    if not await validate_message(message):
        return

    member = await service.get_member(message.from_user.id)
    if member.tbox_available == 0:
        return await message.answer(glob.TBOX_UNAVAILABLE_ERROR)

    await message.reply(
        text=glob.TBOX_TEXT,
        reply_markup=await one_btn_keyboard(
            text=glob.OPEN_TBOX_BTN,
            callback_name=glob.TBOX_OPEN_CALLBACK,
            sender_lock=member.user_id
        )
    )


@router.callback_query(F.data.contains(glob.TBOX_OPEN_CALLBACK))
async def tbox_open(callback: CallbackQuery):
    if not callback.data:
        return await callback.answer(glob.CALLBACK_EXPIRED, show_alert=True)

    sender_id, = ldecode_cbdata(
        data=callback.data,
        binding_types=[int]
    )

    if callback.from_user.id != sender_id:
        return await callback.answer(glob.ALERT_CALLBACK_ACTION, show_alert=True)

    response = await service.tbox(sender_id)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(response)
    await callback.answer()
