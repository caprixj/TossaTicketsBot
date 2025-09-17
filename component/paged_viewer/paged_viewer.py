import functools
from typing import Callable, Union
from uuid import UUID

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from service import service_core as service
from resources import glob
from service.cbdata.encoding import encode_cbdata, ldecode_cbdata


class PagedViewer:
    def __init__(self, title: str, data_extractor: functools.partial, page_generator: Callable, page_message: Message,
                 start_text: str = None, parse_mode: ParseMode = ParseMode.MARKDOWN):
        self.title = title
        self.start_text = start_text
        self.data_extractor = data_extractor
        self.page_generator = page_generator
        self.page_message = page_message
        self.parse_mode = parse_mode

        self.current_page_number: int = 1
        self.pages: list[str] = []

        self.start_message: Union[Message, None] = None

    async def view(self, operation_id: UUID):
        data = await self.data_extractor()
        self.pages = await self.page_generator(data, self.title)

        if self.has_start_message():
            self.start_message = await self.page_message.answer(
                text=self.start_text,
                parse_mode=self.parse_mode
            )

        await self.page_message.answer(
            text=self.pages[0],
            parse_mode=self.parse_mode,
            reply_markup=await self.reply_markup(
                operation_id=operation_id,
                sender_id=self.page_message.from_user.id
            )
        )

    def has_start_message(self):
        return self.start_text is not None

    def get_page(self):
        return self.pages[self.current_page_number - 1]

    def page_back(self):
        self.current_page_number = self.current_page_number - 1 \
            if self.current_page_number > 1 else len(self.pages)

    def page_forward(self):
        self.current_page_number = self.current_page_number + 1 \
            if self.current_page_number < len(self.pages) else 1

    async def reply_markup(self, operation_id: UUID, sender_id: int) -> InlineKeyboardMarkup:
        async def _build_btn(btn_text: str, callback_name: str) -> InlineKeyboardButton:
            return InlineKeyboardButton(
                text=btn_text,
                callback_data=encode_cbdata(
                    signature=callback_name,
                    data={
                        'sender_id': sender_id,
                        'operation_id': operation_id
                    }
                )
            )

        builder = InlineKeyboardBuilder()
        builder.row(
            await _build_btn(
                btn_text='<<',
                callback_name=glob.PV_BACK_CALLBACK
            ),
            await _build_btn(
                btn_text=f'{self.current_page_number} / {len(self.pages)}',
                callback_name=glob.DECORATIVE_KEYBOARD_BUTTON
            ),
            await _build_btn(
                btn_text='>>',
                callback_name=glob.PV_FORWARD_CALLBACK
            )
        )
        builder.row(await _build_btn(
            btn_text=glob.HIDE_BTN,
            callback_name=glob.PV_HIDE_CALLBACK
        ))

        return builder.as_markup()


async def phide(callback: CallbackQuery):
    sender_id, operation_id = ldecode_cbdata(
        data=callback.data,
        binding_types=[int, UUID]
    )

    if callback.from_user.id != sender_id:
        await callback.answer(glob.ALERT_CALLBACK_ACTION, show_alert=True)
        return

    viewer: PagedViewer = await service.som().run(operation_id)

    await service.som().cancel(operation_id)

    if viewer.has_start_message():
        await viewer.start_message.delete()

    await callback.message.delete()
    await callback.answer()


async def pmove(callback: CallbackQuery, move: str):
    sender_id, operation_id = ldecode_cbdata(
        data=callback.data,
        binding_types=[int, UUID]
    )

    if callback.from_user.id != sender_id:
        await callback.answer(glob.ALERT_CALLBACK_ACTION, show_alert=True)
        return

    viewer: PagedViewer = await service.som().run(operation_id)

    if move == glob.PV_BACK_CALLBACK:
        viewer.page_back()
    elif move == glob.PV_FORWARD_CALLBACK:
        viewer.page_forward()

    operation_id = await service.som().reg(
        func=functools.partial(lambda: viewer),
        operation_id=operation_id,
        asynchronous=False
    )

    try:
        await callback.message.edit_text(
            text=viewer.get_page(),
            parse_mode=viewer.parse_mode
        )
        await callback.message.edit_reply_markup(
            reply_markup=await viewer.reply_markup(
                operation_id=operation_id,
                sender_id=sender_id
            )
        )
        await callback.answer()
    except TelegramRetryAfter as _:
        await callback.answer(glob.CALLBACK_FLOOD_CONTROL, show_alert=True)
