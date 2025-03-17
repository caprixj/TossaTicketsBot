import functools
from datetime import datetime

from aiogram.types import Message


class ServiceOperation:
    def __init__(self, func: functools.partial, command_message: Message):
        self.id = int(datetime.now().timestamp() * 1e6)
        self.func: functools.partial = func
        self.command_message = command_message

    async def run(self):
        return await self.func()
