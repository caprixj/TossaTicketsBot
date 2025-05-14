import functools
from typing import Callable, List, Union

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from service import service_core as service
from resources.const import glob
from command.routed.callbacks.custom_callback_data import get_operation_callback_data, OperationCallbackData


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
        self.pages: List[str] = []

        self.start_message: Union[Message, None] = None

    async def view(self, operation_id: int):
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
            reply_markup=self.reply_markup(
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

    def reply_markup(self, operation_id: int, sender_id: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        back = OperationCallbackData(glob.PV_BACK_CALLBACK, sender_id, operation_id)
        forward = OperationCallbackData(glob.PV_FORWARD_CALLBACK, sender_id, operation_id)
        builder.row(
            InlineKeyboardButton(text='<<', callback_data=back.tostr()),
            InlineKeyboardButton(
                text=f'{self.current_page_number} / {len(self.pages)}',
                callback_data=glob.DECORATIVE_KEYBOARD_BUTTON
            ),
            InlineKeyboardButton(text='>>', callback_data=forward.tostr()),
        )

        hide = OperationCallbackData(glob.PV_HIDE_CALLBACK, sender_id, operation_id)
        builder.row(InlineKeyboardButton(text=glob.HIDE_BTN, callback_data=hide.tostr()))

        return builder.as_markup()


async def keep_paged_viewer(viewer: PagedViewer) -> PagedViewer:
    return viewer


async def phide(callback: CallbackQuery):
    data = await get_operation_callback_data(callback.data)

    if callback.from_user.id != data.sender_id:
        await callback.answer(glob.ALERT_CALLBACK_ACTION, show_alert=True)
        return

    viewer: PagedViewer = await service.operation_manager.run(data.operation_id)

    await service.operation_manager.cancel(data.operation_id)

    if viewer.has_start_message():
        await viewer.start_message.delete()

    await callback.message.delete()
    await callback.answer()


async def pmove(callback: CallbackQuery, move: str):
    data = await get_operation_callback_data(callback.data)

    if callback.from_user.id != data.sender_id:
        await callback.answer(glob.ALERT_CALLBACK_ACTION, show_alert=True)
        return

    viewer: PagedViewer = await service.operation_manager.run(data.operation_id)

    if move == glob.PV_BACK_CALLBACK:
        viewer.page_back()
    elif move == glob.PV_FORWARD_CALLBACK:
        viewer.page_forward()
    else:
        raise RuntimeError('pmove(callback: CallbackQuery, move: str): invalid move')

    await service.operation_manager.register(
        func=functools.partial(keep_paged_viewer, viewer),
        operation_id=data.operation_id
    )

    try:
        await callback.message.edit_text(
            text=viewer.get_page(),
            parse_mode=viewer.parse_mode
        )
        await callback.message.edit_reply_markup(
            reply_markup=viewer.reply_markup(
                operation_id=data.operation_id,
                sender_id=data.sender_id
            )
        )
        await callback.answer()
    except TelegramRetryAfter as _:
        await callback.answer(glob.CALLBACK_FLOOD_CONTROL, show_alert=True)
