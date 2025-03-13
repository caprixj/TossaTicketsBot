import functools
from datetime import datetime


class ServiceOperation:
    def __init__(self, func: functools.partial):
        self.id = int(datetime.now().timestamp() * 1e6)
        self.func: functools.partial = func

    async def run(self):
        return await self.func()
