from aiogram import BaseMiddleware
from aiogram.types import Message

from utilities.global_vars import GlobalVariables as gv


class SourceFilterMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        if event.chat.type == "private" or event.chat.id == gv.rms.group_chat_id:
            return await handler(event, data)

        return
