from aiogram import BaseMiddleware
from aiogram.types import Message

import resources.const.glob as glob
from resources.funcs.funcs import get_current_datetime


class SourceFilterMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        if event.chat.type == 'private' or glob.rms.allowed_chat(event.chat.id):
            print(f"{'private ' + str(event.chat.id) if event.chat.type == 'private' else '(super)group'} - "
                  f"{get_current_datetime()}: {event.text if event.text and event.text.startswith('/') else ''}")
            return await handler(event, data)
