from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from command.util.validations import validate_message
from command.parser.types.command_list import CommandList as CL

router = Router()


@router.message(Command(CL.rusni.name))
async def rusni(message: Message):
    await validate_message(message)
    await message.answer(glob.RUSNI_TEXT)


@router.message(Command(CL.rustni.name))
async def rustni(message: Message):
    await rusni(message)
