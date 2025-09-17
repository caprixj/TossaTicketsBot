from aiogram import Router, F
from aiogram.types import CallbackQuery

from resources import glob

router = Router()


@router.callback_query(F.data.contains(glob.HIDE_CALLBACK))
async def hide(callback: CallbackQuery):
    await callback.message.delete()
