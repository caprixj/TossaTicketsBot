import functools
from datetime import datetime

from aiogram.types import Message


class ServiceOperation:
    def __init__(self, func: functools.partial, command_message: Message = None, operation_id: int = -1):
        self.id = int(datetime.now().timestamp() * 1e6) \
            if operation_id == -1 else operation_id
        self.func: functools.partial = func
        self.command_message = command_message

    async def run(self):
        return await self.func()
