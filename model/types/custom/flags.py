from model.types.custom.base import TicketonomicsType


class Flag(TicketonomicsType):
    ID = 'flag'
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self) -> str:
        return self.data

    async def const_cast(self, const: str):
        if self.data == const:
            return self.data
        else:
            raise ValueError()


class PercentFlag(Flag):
    ID = 'percent-flag'
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self) -> str:
        return await super().const_cast('%')


class IdFlag(Flag):
    ID = 'id-flag'
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self) -> str:
        return await super().const_cast('id')


class BanFlag(Flag):
    ID = 'ban-flag'
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self) -> str:
        return await super().const_cast('ban')


class AdminFlag(Flag):
    ID = 'admin-flag'
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self) -> str:
        return await super().const_cast('-a')
