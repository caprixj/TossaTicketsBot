from abc import abstractmethod, ABC
from dataclasses import dataclass


@dataclass
class CustomCallbackData(ABC):
    callback_name: str
    sender_id: int

    @abstractmethod
    def tostr(self):
        pass


@dataclass
class OperationCallbackData(CustomCallbackData):
    operation_id: int = -1

    def tostr(self):
        return f'{self.callback_name}\t{self.sender_id}\t{self.operation_id}'


@dataclass
class MsellCallbackData(CustomCallbackData):
    emoji: str
    quantity: int

    def tostr(self):
        return f'{self.callback_name}\t{self.sender_id}\t{self.emoji}\t{self.quantity}'


async def get_operation_callback_data(data: str) -> OperationCallbackData:
    s = data.split('\t')
    return OperationCallbackData(
        callback_name=s[0],
        sender_id=int(s[1]),
        operation_id=int(s[2])
    )


async def get_msell_callback_data(data: str) -> MsellCallbackData:
    s = data.split('\t')
    return MsellCallbackData(
        callback_name=s[0],
        sender_id=int(s[1]),
        emoji=s[2],
        quantity=int(s[3])
    )
