import functools
from typing import Optional

from aiogram.types import Message

from service.service_operation import ServiceOperation


class ServiceOperationManager:
    def __init__(self):
        self.operations: list[ServiceOperation] = list()

    async def register(self, *args, func, command_message: Message) -> int:
        op = ServiceOperation(
            func=functools.partial(func, *args),
            command_message=command_message
        )
        self.operations.append(op)
        return op.id

    async def run(self, operation_id: int) -> Optional:
        op = self._get_op(operation_id)

        if op is None:
            return None

        self.operations.remove(op)
        return await op.run()

    async def cancel(self, operation_id: int) -> None:
        op = self._get_op(operation_id)

        if op is None:
            return

        self.operations.remove(op)

    async def get_command_message(self, operation_id: int) -> Optional[Message]:
        op = self._get_op(operation_id)

        if op is None:
            return None

        return op.command_message

    def _get_op(self, operation_id: int) -> Optional[ServiceOperation]:
        for op in self.operations:
            if op.id == operation_id:
                return op
        return None
