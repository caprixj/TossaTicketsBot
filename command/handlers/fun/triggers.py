from aiogram import Router, F
from aiogram.types import Message

import resources.glob as glob
from service import service_core as service

router = Router()


@router.message(F.text.regexp(r'^[дД]+[аА]+[.]*[!]*[?]*$'))
async def da(message: Message):
    await message.answer(f'пиз{message.text}')


@router.message(F.text.regexp(r'^[нН]+[єЄ]+[.]*[!]*[?]*$'))
async def nie_ua(message: Message):
    await message.answer(f'рука в гав{message.text}!')


@router.message(F.text.regexp(r'^[нН]+[еЕ]+[.]*[!]*[?]*$'))
async def nie_ru(message: Message):
    await message.answer(f'рука в гов{message.text}!')


@router.message(F.text.regexp(r'сфс|СФС|sfs|SFS'))
async def sfs_alert_trigger(message: Message):
    if await service.get_sfs_alert_message(message.chat.id) is not None:
        await message.reply(glob.SFS_ALERT_TRIGGER_RESPONSE)
        await message.answer_sticker(glob.CRYING_STICKER_FILE_ID)
