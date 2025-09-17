from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from command.parser.types.command_list import CommandList as CL
from resources import glob

router = Router()


@router.message(Command(CL.cancel.name))
async def cancel(message: Message, state: FSMContext):
    if await state.get_data():
        await state.clear()
        await message.answer(glob.FLOW_CANCELED)
    else:
        await message.answer(glob.NOTHING_TO_CANCEL)
