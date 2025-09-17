from model.types.custom.base import TicketonomicsType
from repository import repository_core as repo


class EmployeePosition(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self):
        for j in await repo.get_jobs():
            if self.data == j.position:
                return self.data

        raise ValueError()
