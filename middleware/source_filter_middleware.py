import utilities.globals as glob

from aiogram import BaseMiddleware
from aiogram.enums import ContentType
from aiogram.types import Message


async def _is_accepted_content_type(event: Message) -> bool:
    return event.content_type in [
        ContentType.TEXT,
        ContentType.LEFT_CHAT_MEMBER,
        ContentType.NEW_CHAT_MEMBERS
    ]


class SourceFilterMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        if event.chat.type == "private" or event.chat.id == glob.rms.group_chat_id:
            if await _is_accepted_content_type(event):
                return await handler(event, data)
        return
