from aiogram import BaseMiddleware
from aiogram.types import Message

import resources.glob as glob
from resources.funcs import utcnow_str


class SourceFilterMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        if event.chat.type == 'private' or glob.rms.is_whitelist_chat(event.chat.id):
            print(f"{'private ' + str(event.chat.id) if event.chat.type == 'private' else 'group'} - "
                  f"{utcnow_str()}: {event.text if event.text and event.text.startswith('/') else ''}")
            return await handler(event, data)
