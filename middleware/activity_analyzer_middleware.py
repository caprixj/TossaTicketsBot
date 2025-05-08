from aiogram import BaseMiddleware
from aiogram.types import Message

from service import activity_analyzer
import resources.const.glob as glob


async def _message_important(m: Message) -> bool:
    return m.chat.id == glob.rms.group_chat_id and not m.from_user.is_bot


class ActivityAnalyzerMiddleware(BaseMiddleware):
    async def __call__(self, handler, message: Message, data: dict):
        if await _message_important(message):
            await activity_analyzer.save(message)

        return await handler(message, data)
