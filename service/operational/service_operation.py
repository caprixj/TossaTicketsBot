import functools
import uuid
from uuid import UUID
from typing import Any


class ServiceOperation:
    def __init__(self,
                 func: functools.partial,
                 data: dict[str, Any] = None,
                 operation_id: UUID = None,
                 asynchronous: bool = True):
        self.id: UUID = operation_id if operation_id else uuid.uuid4()
        self.func = func
        self.data = data
        self.asynchronous = asynchronous

    async def run(self):
        return await self.func() if self.asynchronous else self.func()
