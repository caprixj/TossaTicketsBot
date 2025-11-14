from aiogram import Router, F
from aiogram.types import Message

import resources.glob as glob
from service import service_core as service

router = Router()


@router.message(F.text.regexp(r'Рустні|рустні|Рустне|рустне'))
async def rustni(message: Message):
    await message.answer('пизда')


@router.message(F.text.regexp(r'Нєгр|нєгр|Укроп|укроп'))
async def nigga(message: Message):
    if 'нєгр' in message.text.lower():
        await message.answer(f'нєгр син шлюхи')
    else:
        await message.answer(f'укроп син шлюхи')


@router.message(F.text.regexp(r'сфс|СФС|sfs|SFS'))
async def sfs_alert_trigger(message: Message):
    if await service.get_sfs_alert_message(message.chat.id) is not None:
        await message.reply(glob.SFS_ALERT_TRIGGER_RESPONSE)
        await message.answer_sticker(glob.CRYING_STICKER_FILE_ID)
