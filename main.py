import asyncio
import logging
import os
import sys
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram.utils.keyboard import InlineKeyboardBuilder

import utilities.globals as glob

import aiosqlite
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, LinkPreviewOptions

import comparser.standard_overloads as sol
from comparser.results.com_handler_result import CommandHandlerResult
from comparser.com_parser import CommandParser
from comparser.overload import Overload
from comparser.enums.param_type import ParamType as pt
from comparser.enums.com_list import CommandList as cl
from comparser.enums.cpr_messages import CommandParserResultMessages
from middleware.source_filter_middleware import SourceFilterMiddleware
from model.database.transactions.transaction_result import TransactionResult
from model.database.transactions.tr_messages import TransactionResultMessages as trem
from repository.repository_core import Repository
from service.service_core import Service
from utilities.callback_utils import generate_callback_data, get_callback_data
from utilities.run_mode import RunMode
from utilities.glob_func import get_random_permission_denied_message, get_run_mode_settings, get_db_setup_sql_script, \
    get_formatted_name_by_member, get_fee

service = Service()
dp = Dispatcher()


@dp.message(Command(cl.sql.name))
async def sql(message: Message):
    # /sql <query:text>
    o = Overload(creator_filter=True).add_param(sol.QUERY, pt.text)

    cp = CommandParser(message, o)
    result = await cp.parse()

    if not result.valid:
        await _respond_invalid(message, result.error_message)
        return

    (executed, response) = await service.execute_sql(
        query=result.params.get(sol.QUERY)
    )

    status = glob.SQL_SUCCESS_TEXT if executed else glob.SQL_FAILED_TEXT
    await message.reply(f'{status}\n\n{response}', parse_mode=None)


@dp.message(Command(cl.addt.name))
async def addt(message: Message):
    result = await count_handler(
        message=message,
        count_type=pt.pnreal,
        creator_filter=True
    )

    if not result.valid:
        return

    await service.add_tickets(
        member=result.target_member,
        tickets=result.get_param(sol.COUNT),
        description=result.get_param(sol.DESCRIPTION)
    )

    await message.answer(glob.ADDT_TEXT)


@dp.message(Command(cl.delt.name))
async def delt(message: Message):
    result = await count_handler(
        message=message,
        count_type=pt.pnreal,
        creator_filter=True
    )

    if not result.valid:
        return

    await service.delete_tickets(
        member=result.target_member,
        tickets=result.get_param(sol.COUNT),
        description=result.get_param(sol.DESCRIPTION)
    )

    await message.answer(glob.DELT_TEXT)


@dp.message(Command(cl.sett.name))
async def sett(message: Message):
    result = await count_handler(
        message=message,
        count_type=pt.real,
        creator_filter=True
    )

    if not result.valid:
        return

    await service.set_tickets(
        member=result.target_member,
        tickets=result.get_param(sol.COUNT),
        description=result.get_param(sol.DESCRIPTION)
    )

    await message.answer(glob.SETT_TEXT)


@dp.message(Command(cl.help.name))
async def help_(message: Message):
    await message.answer(
        text=glob.HELP_TEXT,
        parse_mode=ParseMode.MARKDOWN,
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )


@dp.message(Command(cl.topt.name))
async def topt(message: Message):
    # /topt
    o_no_size = Overload(name='no-size')

    # /topt <size:nint>
    o_size = Overload(name='size').add_param(sol.SIZE, pt.nint)

    cpr = await CommandParser(message, o_no_size, o_size).parse()

    if not cpr.valid:
        await _respond_invalid(message, cpr.error_message)
        return

    async def _match_overload():
        return await service.get_tickets_top() if cpr.overload.name == o_no_size.name \
            else await service.get_tickets_top_by_size(cpr.params.get(sol.SIZE))

    await service.validate_member(message.from_user)
    response = await _match_overload()
    await message.answer(response)


@dp.message(Command(cl.bal.name))
async def bal(message: Message):
    result = await empty_handler(message)

    if not result.valid:
        return

    response = await service.get_member_balance(result.target_member)
    await message.answer(response)


@dp.message(Command(cl.infm.name))
async def infm(message: Message):
    result = await empty_handler(message)

    if not result.valid:
        return

    response = await service.get_member_info(result.target_member.user_id)
    await message.answer(response, parse_mode=ParseMode.HTML)


def tpay_confirm_keyboard(op_id: int, sender_id: int):
    builder = InlineKeyboardBuilder()

    cd_yes = generate_callback_data(glob.TPAY_YES_CALLBACK, op_id, sender_id)
    if cd_yes is None:
        raise RuntimeError(glob.GENERATE_CALLBACK_DATA_ERROR_TEXT)
    builder.row(InlineKeyboardButton(text='✅ Продовжити', callback_data=cd_yes))

    cd_no = generate_callback_data(glob.TPAY_NO_CALLBACK, op_id, sender_id)
    if cd_no is None:
        raise RuntimeError(glob.GENERATE_CALLBACK_DATA_ERROR_TEXT)
    builder.row(InlineKeyboardButton(text='❌ Скасувати', callback_data=cd_no))

    return builder.as_markup()


@dp.message(Command(cl.tpay.name))
async def tpay(message: Message):
    chr_ = await count_handler(message, pt.pnreal, self_reply_filter=True)

    if not chr_.valid:
        return

    sender = await service.get_member_by_user(message.from_user)

    if sender.tpay_available == 0:
        await message.answer(trem.tpay_unavailable)
        return

    receiver = chr_.target_member
    transfer = chr_.get_param(sol.COUNT)
    fee = await get_fee(transfer)
    total = transfer + fee
    description = chr_.get_param(sol.DESCRIPTION)

    tpay_confirm_text = (f'відправник: {await get_formatted_name_by_member(sender, ping=True)}\n'
                         f'отримувач: {await get_formatted_name_by_member(receiver, ping=True)}\n\n'
                         f'*загальна сума: {total:.2f}*\n'
                         f'сума переводу: {transfer:.2f}\n'
                         f'комісія: {fee:.2f} (37%, min 1.00)\n\n'
                         f'опис: _{description}_')

    op_id = await service.operation_manager.register(
        service.tpay, sender, receiver, transfer, description
    )

    await message.answer(tpay_confirm_text, reply_markup=tpay_confirm_keyboard(op_id, sender.user_id))


@dp.callback_query(lambda c: c.data.startswith(glob.TPAY_YES_CALLBACK))
async def tpay_yes(callback: CallbackQuery):
    op_id_str, sender_id_str = await get_callback_data(callback.data)
    op_id = int(op_id_str)
    sender_id = int(sender_id_str)
    message_id = callback.message.message_id

    if message_id in service.active_callbacks:
        await callback.answer(glob.ALERT_CALLBACK_ACTIVE_TEXT, show_alert=True)
        return

    service.active_callbacks.append(message_id)

    if callback.from_user.id != sender_id:
        await callback.answer(glob.ALERT_CALLBACK_YES_TEXT, show_alert=True)
        return

    tr_: Optional[TransactionResult] = await service.operation_manager.run(op_id)

    if tr_ is None:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(glob.SERVICE_OPERATION_NONE_RESULT_TEXT)
        service.active_callbacks.remove(message_id)
        return

    if not tr_.valid:
        await callback.message.answer(tr_.message)
        await callback.message.delete()
        service.active_callbacks.remove(message_id)
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.reply(glob.TPAY_TEXT)
    await callback.answer()
    service.active_callbacks.remove(message_id)


@dp.callback_query(lambda c: c.data.startswith(glob.TPAY_NO_CALLBACK))
async def tpay_no(callback: CallbackQuery):
    op_id_str, sender_id_str = await get_callback_data(callback.data)
    op_id = int(op_id_str)
    sender_id = int(sender_id_str)

    if callback.from_user.id != sender_id:
        await callback.answer(glob.ALERT_CALLBACK_NO_TEXT, show_alert=True)
        return

    await service.operation_manager.cancel(op_id)
    await callback.message.delete()
    await callback.answer()


# [<reply>] /command
# /command <username:username>
# /command <user_id:pnint>
async def empty_handler(message: Message) -> CommandHandlerResult:
    overloads = [
        await sol.reply_empty(reply_optional=True),
        await sol.username_empty(),
        await sol.user_id_empty()
    ]

    cp = CommandParser(message, *overloads)
    cpr = await cp.parse()

    if not cpr.valid:
        await _respond_invalid(message, cpr.error_message)
        return CommandHandlerResult()

    user = message.from_user \
        if message.reply_to_message is None \
        else message.reply_to_message.from_user

    target_member = await service.get_member_by_cpr(cpr, user)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED_TEXT)
        return CommandHandlerResult()

    return CommandHandlerResult(target_member, cpr, valid=True)


# <reply> /command <count:any> [<description:text>]
# /command <username:username> <count:any> [<description:text>]
# /command <user_id:pnint> <count:any> [<description:text>]
async def count_handler(
        message: Message,
        count_type: pt,
        creator_filter: bool = False,
        self_reply_filter: bool = False) -> CommandHandlerResult:
    overloads = [
        await sol.reply_count(
            count_type=count_type,
            creator_filter=creator_filter,
            self_reply_filter=self_reply_filter
        ),
        await sol.username_count(pt.pnint, creator_filter=creator_filter),
        await sol.user_id_count(pt.pnint, creator_filter=creator_filter)
    ]

    cp = CommandParser(message, *overloads)
    cpr = await cp.parse()

    if not cpr.valid:
        await _respond_invalid(message, cpr.error_message)
        return CommandHandlerResult()

    user = message.reply_to_message.from_user if message.reply_to_message is not None else None
    target_member = await service.get_member_by_cpr(cpr, user)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED_TEXT)
        return CommandHandlerResult()

    return CommandHandlerResult(target_member, cpr, valid=True)


async def _create_databases():
    os.makedirs(os.path.dirname(glob.rms.db_file_path), exist_ok=True)
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        for query in await get_db_setup_sql_script():
            await db.execute(query)
            await db.commit()


async def _define_run_mode() -> RunMode:
    if len(sys.argv) <= 1:
        return RunMode.DEFAULT

    arg = sys.argv[1]

    if arg == RunMode.DEV.value:
        return RunMode.DEV
    elif arg == RunMode.PROD.value:
        return RunMode.PROD


async def _define_rms(rm: RunMode) -> bool:
    if rm not in [RunMode.PROD, RunMode.DEV]:
        return False

    glob.rms = await get_run_mode_settings(rm)
    return True


async def _define_service():
    global service
    service = Service(Repository(glob.rms.db_file_path))


async def _respond_invalid(message: Message, response: CommandParserResultMessages):
    out_message = await get_random_permission_denied_message() \
        if response == CommandParserResultMessages.not_creator else response

    await message.reply(out_message)


async def main():
    run_mode = await _define_run_mode()
    valid_args = await _define_rms(run_mode)
    scheduler = AsyncIOScheduler()

    if not valid_args:
        raise RuntimeError(glob.VALID_ARGS_TEXT)

    await _define_service()
    await _create_databases()

    service.bot = Bot(token=glob.rms.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp.message.middleware(SourceFilterMiddleware())

    scheduler.add_job(service.reset_tpay_available, 'cron', hour=0, minute=0)
    scheduler.start()

    await dp.start_polling(service.bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


# @dp.message(Command(cl.db.name))
# async def db(message: Message) -> None:
#     await service.bot.send_document(
#         chat_id=glob.rms.group_chat_id,
#         document=FSInputFile(glob.rms.db_file_path)
#     )
