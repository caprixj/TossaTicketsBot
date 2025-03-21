import asyncio
import logging
import sys
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, LinkPreviewOptions, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import utilities.glob as glob
from comparser import cog
from comparser.overload import CommandOverload, CommandOverloadGroup
from comparser.parser import CommandParser
from comparser.types.arg_type import Text, Real, PNReal, NInt
from comparser.types.com_list import CommandList as cl
from comparser.types.target_type import CommandTargetType as ctt
from middleware.source_filter_middleware import SourceFilterMiddleware
from model.database.transactions.tr_messages import TransactionResultErrors as tre
from model.database.transactions.transaction_result import TransactionResult
from service.service_core import Service, _get_transaction_time
from utilities.callback.funcs import generate_callback_data, get_callback_data
from utilities.funcs import get_run_mode_settings, get_formatted_name_by_member, get_fee, \
    get_transfer_by_total, create_databases, reply_by_crv
from utilities.run_mode import RunMode

service = Service()
dp = Dispatcher()

""" Creator commands """


@dp.message(Command(cl.sql.name))
async def sql(message: Message):
    og = CommandOverloadGroup(
        # /sql <query:text>
        overloads=[CommandOverload().add(glob.QUERY_ARG, Text)],
        creator_required=True
    )

    cpr = CommandParser(message, og).parse()

    if not cpr.valid:
        await reply_by_crv(message, cpr)
        return

    (executed, response) = await service.execute_sql(
        query=cpr.args[glob.QUERY_ARG]
    )

    status = glob.SQL_SUCCESS if executed else glob.SQL_FAILED
    await message.reply(f'{status}\n\n{response}', parse_mode=None)


@dp.message(Command(cl.addt.name))
async def addt(message: Message):
    cpr = CommandParser(message, cog.tickets(PNReal, creator_required=True)).parse()

    if not cpr.valid:
        await reply_by_crv(message, cpr)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED)
        return

    await service.add_tickets(
        member=target_member,
        tickets=cpr.args[glob.TICKETS_ARG],
        description=cpr.args.get(glob.DESCRIPTION_ARG, None)
    )

    await message.answer(glob.ADDT_TEXT)


@dp.message(Command(cl.delt.name))
async def delt(message: Message):
    cpr = CommandParser(message, cog.tickets(PNReal, creator_required=True)).parse()

    if not cpr.valid:
        await reply_by_crv(message, cpr)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED)
        return

    await service.delete_tickets(
        member=target_member,
        tickets=cpr.args[glob.TICKETS_ARG],
        description=cpr.args.get(glob.DESCRIPTION_ARG, None)
    )

    await message.answer(glob.DELT_TEXT)


@dp.message(Command(cl.sett.name))
async def sett(message: Message):
    cpr = CommandParser(message, cog.tickets(Real, creator_required=True)).parse()

    if not cpr.valid:
        await reply_by_crv(message, cpr)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED)
        return

    await service.set_tickets(
        member=target_member,
        tickets=cpr.args[glob.TICKETS_ARG],
        description=cpr.args.get(glob.DESCRIPTION_ARG, None)
    )

    await message.answer(glob.SETT_TEXT)


@dp.message(Command(cl.sfs.name))
async def sfs(message: Message):
    og = CommandOverloadGroup(
        # /sfs <message:text>
        overloads=[CommandOverload().add(glob.MESSAGE_ARG, Text)],
        creator_required=True
    )

    cpr = CommandParser(message, og).parse()

    if not cpr.valid:
        await reply_by_crv(message, cpr)
        return

    await service.bot.send_message(
        chat_id=glob.rms.group_chat_id,
        text=cpr.args[glob.MESSAGE_ARG]
    )


@dp.message(Command(cl.db.name))
async def db(message: Message) -> None:
    og = CommandOverloadGroup(
        # /db
        overloads=[CommandOverload()],
        creator_required=True
    )

    cpr = CommandParser(message, og).parse()

    if not cpr.valid:
        await reply_by_crv(message, cpr)
        return

    await service.bot.send_document(
        chat_id=message.chat.id,
        document=FSInputFile(glob.rms.db_file_path)
    )


""" Member commands """


@dp.message(Command('lymik'))
async def lymik(message: Message):
    await service.get_tickets_top()
    print(f'lymik - {_get_transaction_time()}')


@dp.message(Command(cl.reg.name))
async def reg(message: Message):
    og = CommandOverloadGroup([
        # /reg
        CommandOverload(),
        # <reply> /reg
        CommandOverload(reply_required=True)
    ])

    cpr = CommandParser(message, og).parse()

    if not cpr.valid:
        await message.answer(glob.COM_PARSER_FAILED)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        if cpr.overload.target_type == ctt.none:
            await service.create_member(message.from_user)
        elif cpr.overload.target_type == ctt.reply:
            await service.create_member(message.reply_to_message.from_user)
        await message.answer(glob.REG_SUCCESS)
    else:
        if cpr.overload.target_type == ctt.none:
            await service.update_member(message.from_user, target_member)
            await message.answer(glob.REG_DENIED_CTT_NONE)
        elif cpr.overload.target_type == ctt.reply:
            await service.update_member(message.reply_to_message.from_user, target_member)
            await message.answer(glob.REG_DENIED_CTT_REPLY)


@dp.message(Command(cl.rusni.name))
async def rusni(message: Message):
    await validate_user(message)
    await message.answer(glob.RUSNI_TEXT)


@dp.message(Command(cl.help.name))
async def help_(message: Message):
    await validate_user(message)
    await message.answer(
        text=glob.HELP_TEXT,
        parse_mode=ParseMode.MARKDOWN,
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )


@dp.message(Command(cl.topt.name))
async def topt(message: Message):
    if not await validate_user(message):
        return

    og = CommandOverloadGroup([
        # /topt
        CommandOverload(),
        # /topt <size:nint>
        CommandOverload().add(glob.SIZE_ARG, NInt)
    ])

    cpr = CommandParser(message, og).parse()

    if not cpr.valid:
        await message.answer(glob.COM_PARSER_FAILED)
        return

    if cpr.overload is og[0]:
        await message.answer(await service.get_tickets_top())
    else:
        size = cpr.args[glob.SIZE_ARG]
        await message.answer(await service.get_tickets_top_by_size(size))


@dp.message(Command(cl.bal.name))
async def bal(message: Message):
    if not await validate_user(message):
        return

    cpr = CommandParser(message, cog.pure()).parse()

    if not cpr.valid:
        await message.answer(glob.COM_PARSER_FAILED)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED)
        return

    response = await service.get_member_balance(target_member)
    await message.answer(response)


@dp.message(Command(cl.infm.name))
async def infm(message: Message):
    if not await validate_user(message):
        return

    cpr = CommandParser(message, cog.pure()).parse()

    if not cpr.valid:
        await message.answer(glob.COM_PARSER_FAILED)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED)
        return

    response = await service.get_member_info(target_member.user_id)
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

    cpr = CommandParser(message, cog.tickets(PNReal, creator_required=False)).parse()

    if not cpr.valid:
        await message.answer(glob.COM_PARSER_FAILED)
        return

    receiver = await service.get_target_member(cpr)

    if receiver is None:
        await message.answer(glob.GET_MEMBER_FAILED)
        return

    sender = await service.get_member(message.from_user.id)

    if sender.tpay_available == 0:
        await message.answer(tre.tpay_unavailable)
        return

    description = cpr.args.get(glob.DESCRIPTION_ARG, None)

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

    total, transfer, fee = await calculate_transfer(cpr.args[glob.TICKETS_ARG])

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
        await callback.answer(glob.ALERT_CALLBACK_YES, show_alert=True)
        return

    tr_: Optional[TransactionResult] = await service.operation_manager.run(tcd.operation_id)

    if tr_ is None:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(glob.SERVICE_OPERATION_NONE_RESULT)
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
        await callback.answer(glob.ALERT_CALLBACK_NO, show_alert=True)
        return

    await service.operation_manager.cancel(tcd.operation_id)
    await callback.message.delete()
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith(glob.TPAY_FEE_INCORPORATION_CALLBACK))
async def tpay_fi(callback: CallbackQuery):
    tcd = await get_callback_data(callback.data)

    if callback.from_user.id != tcd.sender_id:
        await callback.answer(glob.ALERT_CALLBACK_ACTION, show_alert=True)
        return

    command_message = await service.operation_manager.get_command_message(tcd.operation_id)
    if command_message is None:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(glob.SERVICE_OPERATION_NONE_RESULT)
        return

    await service.operation_manager.cancel(tcd.operation_id)
    await callback.answer()
    await tpay(
        message=command_message,
        callback_message=callback.message,
        fee_incorporated=True
    )


""" Side Functions """


async def validate_user(message: Message) -> bool:
    member = await service.get_member(message.from_user.id)
    member_exists = member is not None

    if member_exists:
        await service.update_member(message.from_user, member)
    else:
        await message.reply(glob.NOT_MEMBER_ERROR)

    return member_exists


async def reset_tpay_available():
    await service.reset_tpay_available()
    await service.bot.send_message(
        chat_id=glob.rms.group_chat_id,
        text=glob.RESET_TPAY_AVAILABLE_DONE
    )


async def db_backup():
    await service.bot.send_document(
        chat_id=glob.rms.db_backup_chat_id,
        document=FSInputFile(glob.rms.db_file_path)
    )
    await service.bot.send_message(
        chat_id=glob.rms.group_chat_id,
        text=glob.DB_BACKUP_DONE
    )


async def schedule_test():
    await service.bot.send_message(
        chat_id=glob.rms.db_backup_chat_id,
        text=_get_transaction_time()
    )


async def schedule(scheduler: AsyncIOScheduler):
    for i in range(0, 144):
        h = int(10 * i / 60)
        m = 10 * i % 60
        scheduler.add_job(schedule_test, 'cron', hour=h, minute=m)

    scheduler.start()


def define_run_mode() -> RunMode:
    if len(sys.argv) <= 1:
        return RunMode.DEFAULT

    arg = sys.argv[1]

    if arg == RunMode.DEV.value:
        return RunMode.DEV
    elif arg == RunMode.PROD.value:
        return RunMode.PROD


def define_rms(rm: RunMode) -> bool:
    if rm not in [RunMode.PROD, RunMode.DEV]:
        return False

    glob.rms = get_run_mode_settings(rm)
    return True


def define_service():
    global service
    service = Service(glob.rms.db_file_path)


async def main():
    run_mode = define_run_mode()
    valid_args = define_rms(run_mode)
    scheduler = AsyncIOScheduler()

    if not valid_args:
        raise RuntimeError(glob.INVALID_ARGS)

    define_service()
    await create_databases()

    service.bot = Bot(
        token=glob.rms.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN
        )
    )

    dp.message.middleware(SourceFilterMiddleware())

    await schedule(scheduler)
    await dp.start_polling(service.bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
