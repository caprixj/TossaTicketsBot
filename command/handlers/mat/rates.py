from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from service import service_core as service
from command.util.validations import validate_message
from component.keyboards.keyboards import hide_keyboard
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(CL.rates.name))
async def rates(message: Message):
    if not await validate_message(message):
        return

    await message.answer(
        text=await service.rates(),
        reply_markup=await hide_keyboard()
    )
