from aiogram import BaseMiddleware
from aiogram.types import Message

from service import activity_analyzer
import resources.glob as glob


async def _message_important(m: Message) -> bool:
    return glob.rms.is_whitelist_chat(m.chat.id) and not m.from_user.is_bot


class ActivityAnalyzerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        if await _message_important(event):
            await activity_analyzer.save(event)

        return await handler(event, data)
