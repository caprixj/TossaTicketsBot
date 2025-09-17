from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, LinkPreviewOptions

import resources.glob as glob
from command.util.validations import validate_user
from component.keyboards.keyboards import hide_keyboard
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(CL.help.name))
async def help_(message: Message):
    await validate_user(message.from_user)
    await message.answer(
        text=glob.HELP_TEXT,
        parse_mode=ParseMode.MARKDOWN,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        reply_markup=await hide_keyboard()
    )
