from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def _catch_all(_: Message):
    pass
