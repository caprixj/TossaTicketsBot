import re
import random
import string
from typing import Type

from model.types.custom.base import TicketonomicsType, eufloat


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


# all double (to int cents)
class RealTickets(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^-?(?:[1-9]\d*|0)(?:[.,]\d{1,2})?$'

    async def cast(self) -> int:
        if bool(re.match(self.pattern, self.data)):
            return round(eufloat(self.data) * 100)
        else:
            raise ValueError()


# all double except zero (to int cents)
class NRealTickets(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^(?!-?0+(?:[.,]0{1,2})?$)-?(?:[1-9]\d*|0)(?:[.,]\d{1,2})?$'

    async def cast(self) -> int:
        if bool(re.match(self.pattern, self.data)):
            return round(eufloat(self.data) * 100)
        else:
            raise ValueError()


# all positive doubles except zero (to int cents)
class PNRealTickets(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^(?!0(?:[.,]0{1,2})?$)(?:[1-9]\d*|0)(?:[.,]\d{1,2})?$'

    async def cast(self) -> int:
        if self.validate():
            return round(eufloat(self.data) * 100)
        else:
            raise ValueError()

    def validate(self) -> bool:
        if not self.data:
            return False
        return bool(re.match(self.pattern, self.data))


# all integers
class Int(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^-?\d+$'

    async def cast(self) -> int:
        if bool(re.match(self.pattern, self.data)):
            return int(self.data)
        else:
            raise ValueError()


# all integers except zero
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
        if self.validate():
            return int(self.data)
        else:
            raise ValueError()

    def validate(self) -> bool:
        if not self.data:
            return False
        return bool(re.match(self.pattern, self.data))


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


class OrderCode(TicketonomicsType):
    def __init__(self, data: str):
        super().__init__(data)
        self.pattern = r'^#?[A-Z]\d{4}$'

    async def cast(self) -> str:
        return self.sync_cast()

    def sync_cast(self):
        if self.validate():
            return self.data.lstrip('#')
        else:
            raise ValueError()

    def validate(self) -> bool:
        if not self.data:
            return False
        return bool(re.match(self.pattern, self.data))

    @staticmethod
    def generate_random():
        return random.choice(string.ascii_uppercase) + ''.join(random.choices(string.digits, k=4))


def xreal(arg_type: Type[TicketonomicsType]) -> bool:
    return arg_type in [
        RealTickets, NRealTickets, PNRealTickets,
        Int, NInt, PNInt
    ]
