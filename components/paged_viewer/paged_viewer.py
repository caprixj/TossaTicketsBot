import functools
from typing import Callable, List, Union

from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from resources.const import glob
from command.routed.callbacks.callback_data import generate_callback_data


class PagedViewer:
    def __init__(self, title: str, start_text: str, data_extractor: functools.partial, page_generator: Callable,
                 page_message: Message, parse_mode: ParseMode = ParseMode.MARKDOWN):
        self.title = title
        self.start_text = start_text
        self.data_extractor = data_extractor
        self.page_generator = page_generator
        self.page_message = page_message
        self.parse_mode = parse_mode

        self.current_page_number: int = 1
        self.pages: List[str] = []

        self.start_message: Union[Message, None] = None

    async def view(self, operation_id: int):
        data = await self.data_extractor()
        self.pages = await self.page_generator(data, self.title)

        self.start_message = await self.page_message.answer(
            text=self.start_text,
            parse_mode=self.parse_mode
        )

        await self.page_message.answer(
            text=self.pages[0],
            parse_mode=self.parse_mode,
            reply_markup=self.reply_markup(
                operation_id=operation_id,
                sender_id=self.page_message.from_user.id
            )
        )

    def get_page(self):
        return self.pages[self.current_page_number - 1]

    def page_back(self):
        self.current_page_number = self.current_page_number - 1 \
            if self.current_page_number > 1 else len(self.pages)

    def page_forward(self):
        self.current_page_number = self.current_page_number + 1 \
            if self.current_page_number < len(self.pages) else 1

    def reply_markup(self, operation_id: int, sender_id: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        back = generate_callback_data(glob.MYTPAY_BACK_CALLBACK, operation_id, sender_id)
        forward = generate_callback_data(glob.MYTPAY_FORWARD_CALLBACK, operation_id, sender_id)
        builder.row(
            InlineKeyboardButton(text='<<', callback_data=back),
            InlineKeyboardButton(
                text=f'{self.current_page_number} / {len(self.pages)}',
                callback_data=glob.DECORATIVE_KEYBOARD_BUTTON
            ),
            InlineKeyboardButton(text='>>', callback_data=forward),
        )

        hide = generate_callback_data(glob.MYTPAY_HIDE_CALLBACK, operation_id, sender_id)
        builder.row(InlineKeyboardButton(text='🗑 Приховати', callback_data=hide))

        return builder.as_markup()


async def keep_paged_viewer(viewer: PagedViewer) -> PagedViewer:
    return viewer
