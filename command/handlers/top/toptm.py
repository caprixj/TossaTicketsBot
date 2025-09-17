from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import resources.glob as glob
from model.types.custom.flags import PercentFlag, IdFlag
from service import service_core as service
from command.util.validations import validate_message
from component.keyboards.keyboards import hide_keyboard
from command.parser.core.overload import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from model.types.custom.primitives import NInt
from command.parser.types.command_list import CommandList as CL
from utils import funcs

router = Router()


@router.message(Command(commands=[CL.topt.name, CL.topm.name]))
async def top(message: Message):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
        # /c
        CommandOverload(oid='pure'),
        # /c <size:nint>
        CommandOverload(oid='size').add(glob.SIZE_ARG, NInt),
        # /c %
        CommandOverload(oid='percent').flag(PercentFlag),
        # /c % <size:nint>
        CommandOverload(oid='percent-size').flag(PercentFlag).add(glob.SIZE_ARG, NInt),
        # /c id
        CommandOverload(oid='id').flag(IdFlag),
        # /c id <size:nint>
        CommandOverload(oid='id-size').flag(IdFlag).add(glob.SIZE_ARG, NInt),
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await message.answer(glob.COM_PARSER_FAILED)

    command_name = funcs.get_command(message)
    if command_name == CL.topt.name:
        logic = service.topt
    elif command_name == CL.topm.name:
        logic = service.topm
    else:
        raise RuntimeError('No command match in rating handler')

    if cpr.overload.oid == 'pure':
        await message.answer(
            text=await logic(),
            reply_markup=await hide_keyboard()
        )
    elif cpr.overload.oid == 'size':
        size = cpr.args[glob.SIZE_ARG]
        await message.answer(
            text=await logic(size=size),
            reply_markup=await hide_keyboard()
        )
    elif cpr.overload.oid == 'percent':
        await message.answer(
            text=await logic(percent_flag=True),
            reply_markup=await hide_keyboard()
        )
    elif cpr.overload.oid == 'percent-size':
        size = cpr.args[glob.SIZE_ARG]
        await message.answer(
            text=await logic(size, percent_flag=True),
            reply_markup=await hide_keyboard()
        )
    elif cpr.overload.oid == 'id':
        await message.answer(
            text=await logic(id_flag=True),
            reply_markup=await hide_keyboard()
        )
    elif cpr.overload.oid == 'id-size':
        size = cpr.args[glob.SIZE_ARG]
        await message.answer(
            text=await logic(size, id_flag=True),
            reply_markup=await hide_keyboard()
        )
