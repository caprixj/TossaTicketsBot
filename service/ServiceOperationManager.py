import functools
from typing import Optional, Union

from service.ServiceOperation import ServiceOperation


class ServiceOperationManager:
    def __init__(self):
        self.operations: list[ServiceOperation] = list()

    async def register(self, func, *args) -> int:
        op = ServiceOperation(functools.partial(func, *args))
        self.operations.append(op)
        return op.id

    async def run(self, operation_id: int) -> Optional:
        op = self._get_op(operation_id)

        if op is None:
            return None

        self.operations.remove(op)
        return await op.run()

    async def cancel(self, operation_id: int):
        op = self._get_op(operation_id)

        if op is None:
            return None

        self.operations.remove(op)

    def _get_op(self, operation_id: int) -> Optional[ServiceOperation]:
        for op in self.operations:
            if op.id == operation_id:
                return op
        return None
