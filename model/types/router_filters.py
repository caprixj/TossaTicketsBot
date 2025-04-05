from aiogram.filters import Filter
from aiogram.types import Message


class TextFilter(Filter):
    def __init__(self, text: str, ignore_case: bool = False) -> None:
        self.text = text
        self.ignore_case = ignore_case

    async def __call__(self, message: Message) -> bool:
        return message.text.lower() == self.text.lower() \
            if self.ignore_case else message.text == self.text
