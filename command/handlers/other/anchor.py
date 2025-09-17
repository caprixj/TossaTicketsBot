from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(CL.anchor.name))
async def anchor(message: Message):
    await message.answer('temporarily disabled')
