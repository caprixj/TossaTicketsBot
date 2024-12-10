from aiogram import BaseMiddleware
from aiogram.types import Message

from utilities.constant import SFS_CHAT_ID


class SourceFilterMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        print(event.chat.type + " " + str(event.chat.id))

        if event.chat.type == "private" or event.chat.id == SFS_CHAT_ID:
            print("ACCEPTED")
            return await handler(event, data)

        print("DENIED")
        return
