import re
from typing import Type

from repository import repository_core as repo


def _eufloat(value: str):
    if isinstance(value, str):
        value = value.replace(",", ".")
    return float(value)


class TicketonomicsType:
    def __init__(self, data: str):
        self.data = data

    async def cast(self):
        return self.data


# any string
class BaseText(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self) -> str:
        return str(self.data)


# any string <= 64 chars
class Text64(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self) -> str:
        if len(self.data) <= 64:
            return self.data
        else:
            raise ValueError()


# any string <= 256 chars
class Text256(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self) -> str:
        if len(self.data) <= 256:
            return self.data
        else:
            raise ValueError()


# any string <= 512 chars
class Text512(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self) -> str:
        if len(self.data) <= 512:
            return self.data
        else:
            raise ValueError()


# any string <= 4096 chars
class Text4096(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self) -> str:
        if len(self.data) <= 4096:
            return self.data
        else:
            raise ValueError()


class ConstArg(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self) -> str:
        return self.data

    async def const_cast(self, const: str):
        if self.data == const:
            return self.data
        else:
            raise ValueError()


class PercentConstArg(ConstArg):
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self) -> str:
        return await super().const_cast('%')


class IdConstArg(ConstArg):
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self) -> str:
        return await super().const_cast('id')


# all double (to int cents)
class RealTickets(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^-?(?:[1-9]\d*|0)(?:[.,]\d{1,2})?$'

    async def cast(self) -> int:
        if bool(re.match(self.pattern, self.data)):
            return round(_eufloat(self.data) * 100)
        else:
            raise ValueError()


# all double except zero (to int cents)
class NRealTickets(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^(?!-?0+(?:[.,]0{1,2})?$)-?(?:[1-9]\d*|0)(?:[.,]\d{1,2})?$'

    async def cast(self) -> int:
        if bool(re.match(self.pattern, self.data)):
            return round(_eufloat(self.data) * 100)
        else:
            raise ValueError()


# all positive double except zero (to int cents)
class PNRealTickets(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^(?!0(?:[.,]0{1,2})?$)(?:[1-9]\d*|0)(?:[.,]\d{1,2})?$'

    async def cast(self) -> int:
        if bool(re.match(self.pattern, self.data)):
            return round(_eufloat(self.data) * 100)
        else:
            raise ValueError()


# all integer
class Int(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^-?\d+$'

    async def cast(self) -> int:
        if bool(re.match(self.pattern, self.data)):
            return int(self.data)
        else:
            raise ValueError()


# all integer except zero
class NInt(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^-?[1-9]\d*$'

    async def cast(self) -> int:
        if bool(re.match(self.pattern, self.data)):
            return int(self.data)
        else:
            raise ValueError()


# all positive integers except zero
class PNInt(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^[1-9]\d*$'

    async def cast(self) -> int:
        if bool(re.match(self.pattern, self.data)):
            return int(self.data)
        else:
            raise ValueError()


class UserID(PNInt):
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self) -> int:
        return await super().cast()


class ChatID(NInt):
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self) -> int:
        return await super().cast()


# @ + text (+ some rules)
class Username(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^@[A-Za-z_][A-Za-z0-9_]{4,}$'

    async def cast(self) -> str:
        if len(self.data) <= 33 and bool(re.match(self.pattern, self.data)):
            return self.data[1:]
        else:
            raise ValueError()


# string id
class SID(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^[a-z]([a-z0-9]{2,15})$'

    async def cast(self) -> str:
        if bool(re.match(self.pattern, self.data)):
            return self.data
        else:
            raise ValueError()


class EmployeePosition(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)

    async def cast(self):
        for j in await repo.get_jobs():
            if self.data == j.position:
                return self.data

        raise ValueError()


def xreal(arg_type: Type[TicketonomicsType]) -> bool:
    return arg_type in [
        RealTickets, NRealTickets, PNRealTickets,
        Int, NInt, PNInt
    ]
