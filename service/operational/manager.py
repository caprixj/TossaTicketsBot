import functools
from uuid import UUID
from typing import Optional, Any

from service.operational.service_operation import ServiceOperation


class ServiceOperationsManager:
    def __init__(self):
        self.operations: list[ServiceOperation] = []

    async def reg(self,
                  func: functools.partial,
                  data: dict[str, Any] = None,
                  operation_id: UUID = None,
                  asynchronous: bool = True) -> UUID:
        op = ServiceOperation(func, data, operation_id, asynchronous)
        self.operations.append(op)
        return op.id

    async def run(self, operation_id: UUID) -> Optional:
        op = self._get_op(operation_id)

        if op is None:
            return None

        self.operations.remove(op)
        return await op.run()

    async def cancel(self, operation_id: UUID):
        op = self._get_op(operation_id)

        if op is None:
            return

        self.operations.remove(op)

    async def get_data(self, operation_id: UUID) -> Optional[dict[str, Any]]:
        op = self._get_op(operation_id)

        if op is None:
            return None

        return op.data

    def _get_op(self, operation_id: UUID) -> Optional[ServiceOperation]:
        for op in self.operations:
            if op.id == operation_id:
                return op
        return None
