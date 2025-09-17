from aiogram import Router, F
from aiogram.types import CallbackQuery

from resources import glob

router = Router()


@router.callback_query(F.data.contains(glob.DECORATIVE_KEYBOARD_BUTTON))
async def decorative_keyboard_button(callback: CallbackQuery):
    await callback.answer()
