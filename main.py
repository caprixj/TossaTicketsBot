import asyncio
import logging
import sys
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram.utils.keyboard import InlineKeyboardBuilder

import utilities.globals as glob

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, LinkPreviewOptions, User

import comparser.standard_overloads as sol
from comparser.results.com_handler_result import CommandHandlerResult
from comparser.com_parser import CommandParser
from comparser.overload import Overload
from comparser.enums.param_type import ParamType as pt
from comparser.enums.com_list import CommandList as cl
from middleware.source_filter_middleware import SourceFilterMiddleware
from model.database.transactions.transaction_result import TransactionResult
from model.database.transactions.tr_messages import TransactionResultMessages as trem
from repository.repository_core import Repository
from service.service_core import Service
from utilities.callback.funcs import generate_callback_data, get_callback_data
from utilities.run_mode import RunMode
from utilities.funcs import get_run_mode_settings, get_formatted_name_by_member, get_fee, \
    get_transfer_by_total, create_databases, respond_invalid

service = Service()
dp = Dispatcher()


@dp.message(Command(cl.sql.name))
async def sql(message: Message):
    if not await validate_user(message):
        return

    # /sql <query:text>
    o = Overload(creator_filter=True).add_param(sol.QUERY, pt.text)

    cp = CommandParser(message, o)
    result = await cp.parse()

    if not result.valid:
        await respond_invalid(message, result)
        return

    (executed, response) = await service.execute_sql(
        query=result.params.get(sol.QUERY)
    )

    status = glob.SQL_SUCCESS_TEXT if executed else glob.SQL_FAILED_TEXT
    await message.reply(f'{status}\n\n{response}', parse_mode=None)


@dp.message(Command(cl.addt.name))
async def addt(message: Message):
    if not await validate_user(message):
        return

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
    if not await validate_user(message):
        return

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
    if not await validate_user(message):
        return

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
    if message.chat.id == glob.rms.group_chat_id:
        if not await validate_user(message):
            return

    await message.answer(
        text=glob.HELP_TEXT,
        parse_mode=ParseMode.MARKDOWN,
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )


@dp.message(Command(cl.topt.name))
async def topt(message: Message):
    if not await validate_user(message):
        return

    # /topt
    o_no_size = Overload(name='no-size')

    # /topt <size:nint>
    o_size = Overload(name='size').add_param(sol.SIZE, pt.nint)

    cpr = await CommandParser(message, o_no_size, o_size).parse()

    if not cpr.valid:
        await respond_invalid(message, cpr)
        return

    async def _match_overload():
        return await service.get_tickets_top() if cpr.overload.name == o_no_size.name \
            else await service.get_tickets_top_by_size(cpr.params.get(sol.SIZE))

    response = await _match_overload()
    await message.answer(response)


@dp.message(Command(cl.bal.name))
async def bal(message: Message):
    if not await validate_user(message):
        return

    result = await empty_handler(message)

    if not result.valid:
        return

    response = await service.get_member_balance(result.target_member)
    await message.answer(response)


@dp.message(Command(cl.infm.name))
async def infm(message: Message):
    if not await validate_user(message):
        return

    result = await empty_handler(message)

    if not result.valid:
        return

    response = await service.get_member_info(result.target_member.user_id)
    await message.answer(response, parse_mode=ParseMode.HTML)


def tpay_keyboard(operation_id: int, sender_id: int, fee_incorporated: bool):
    builder = InlineKeyboardBuilder()

    cd_yes = generate_callback_data(glob.TPAY_YES_CALLBACK, operation_id, sender_id)
    builder.row(InlineKeyboardButton(text='✅ Продовжити', callback_data=cd_yes))

    cd_no = generate_callback_data(glob.TPAY_NO_CALLBACK, operation_id, sender_id)
    builder.row(InlineKeyboardButton(text='❌ Скасувати', callback_data=cd_no))

    if fee_incorporated:
        cd_fi = generate_callback_data(glob.TPAY_FEE_INCORPORATION_CALLBACK, operation_id, sender_id)
        builder.row(InlineKeyboardButton(text='➕ Вкласти комісію', callback_data=cd_fi))

    return builder.as_markup()


@dp.message(Command(cl.tpay.name))
async def tpay(message: Message, callback_message: Message = None, fee_incorporated: bool = False):
    if not await validate_user(message):
        return

    chr_ = await count_handler(message, pt.pnreal, self_reply_filter=True)

    if not chr_.valid:
        return

    sender = await service.get_member_by_user(message.from_user)

    if sender.tpay_available == 0:
        await message.answer(trem.tpay_unavailable)
        return

    receiver = chr_.target_member
    description = chr_.get_param(sol.DESCRIPTION)

    # t - total, x - transfer, f - fee
    # -> (t, x, f)
    async def calculate_transfer(x: float) -> (float, float, float):
        if fee_incorporated:
            t_fi = x
            x_fi = await get_transfer_by_total(t_fi)
            return t_fi, x_fi, t_fi - x_fi
        else:
            f = await get_fee(x)
            return x + f, x, f

    total, transfer, fee = await calculate_transfer(chr_.get_param(sol.COUNT))

    tpay_confirmation_text = (f'відправник: {await get_formatted_name_by_member(sender, ping=True)}\n'
                              f'отримувач: {await get_formatted_name_by_member(receiver, ping=True)}\n\n'
                              f'*загальна сума: {total:.2f}*\n'
                              f'сума переказу: {transfer:.2f}\n'
                              f'комісія: {fee:.2f} ({int(100 * glob.FEE_RATE)}%, min {glob.MIN_FEE:.2f})\n\n'
                              f'опис: _{description}_')

    operation_id = await service.operation_manager.register(
        sender, receiver, transfer, description,
        func=service.tpay,
        command_message=message
    )

    if fee_incorporated:
        await callback_message.edit_text(text=tpay_confirmation_text)
        await callback_message.edit_reply_markup(
            reply_markup=tpay_keyboard(
                operation_id=operation_id,
                sender_id=sender.user_id,
                fee_incorporated=False
            )
        )
    else:
        await message.answer(
            text=tpay_confirmation_text,
            reply_markup=tpay_keyboard(
                operation_id=operation_id,
                sender_id=sender.user_id,
                fee_incorporated=transfer > glob.MIN_FEE
            )
        )


@dp.callback_query(lambda c: c.data.startswith(glob.TPAY_YES_CALLBACK))
async def tpay_yes(callback: CallbackQuery):
    tcd = await get_callback_data(callback.data)

    if callback.from_user.id != tcd.sender_id:
        await callback.answer(glob.ALERT_CALLBACK_YES_TEXT, show_alert=True)
        return

    tr_: Optional[TransactionResult] = await service.operation_manager.run(tcd.operation_id)

    if tr_ is None:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(glob.SERVICE_OPERATION_NONE_RESULT_TEXT)
        return

    if not tr_.valid:
        await callback.message.answer(tr_.message)
        await callback.message.delete()
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.reply(glob.TPAY_TEXT)
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith(glob.TPAY_NO_CALLBACK))
async def tpay_no(callback: CallbackQuery):
    tcd = await get_callback_data(callback.data)

    if callback.from_user.id != tcd.sender_id:
        await callback.answer(glob.ALERT_CALLBACK_NO_TEXT, show_alert=True)
        return

    await service.operation_manager.cancel(tcd.operation_id)
    await callback.message.delete()
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith(glob.TPAY_FEE_INCORPORATION_CALLBACK))
async def tpay_fi(callback: CallbackQuery):
    tcd = await get_callback_data(callback.data)

    if callback.from_user.id != tcd.sender_id:
        await callback.answer(glob.ALERT_CALLBACK_ACTION_TEXT, show_alert=True)
        return

    command_message = await service.operation_manager.get_command_message(tcd.operation_id)
    if command_message is None:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(glob.SERVICE_OPERATION_NONE_RESULT_TEXT)
        return

    await service.operation_manager.cancel(tcd.operation_id)
    await callback.answer()
    await tpay(
        message=command_message,
        callback_message=callback.message,
        fee_incorporated=True
    )


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
        await respond_invalid(message, cpr)
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
        await sol.username_count(
            count_type=count_type,
            creator_filter=creator_filter
        ),
        await sol.user_id_count(
            count_type=count_type,
            creator_filter=creator_filter
        )
    ]

    cp = CommandParser(message, *overloads)
    cpr = await cp.parse()

    if not cpr.valid:
        await respond_invalid(message, cpr)
        return CommandHandlerResult()

    user = message.reply_to_message.from_user if message.reply_to_message is not None else None
    target_member = await service.get_member_by_cpr(cpr, user)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED_TEXT)
        return CommandHandlerResult()

    return CommandHandlerResult(target_member, cpr, valid=True)


async def validate_user(message: Message) -> bool:
    is_member = await is_ticketonomics_member(message.from_user)

    if message.chat.type == 'private':
        if not is_member:
            await message.answer(glob.NOT_TICKETONOMICS_MEMBER_DM_TEXT)
            return False
    elif is_member:
        await service.validate_member(message.from_user)

    return True


async def is_ticketonomics_member(user: User) -> bool:
    return await service.validate_member(user, create=False)


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


async def main():
    run_mode = await _define_run_mode()
    valid_args = await _define_rms(run_mode)
    scheduler = AsyncIOScheduler()

    if not valid_args:
        raise RuntimeError(glob.VALID_ARGS_TEXT)

    await _define_service()
    await create_databases()

    service.bot = Bot(token=glob.rms.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp.message.middleware(SourceFilterMiddleware())

    scheduler.add_job(service.reset_tpay_available, 'cron', hour=0, minute=47)
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
