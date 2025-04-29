from datetime import datetime, timedelta

from aiogram import Bot

from model.database import SalaryPayout
from service import service_core as service
from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import resources.const.glob as glob
from service.price_manager import reset_prices
from service.service_core import payout_salaries
from repository import repository_core as repo

aiosch = AsyncIOScheduler()


async def schedule(bot: Bot):
    aiosch.add_job(_reset_tpay_available, args=[bot], trigger='cron', hour=0, minute=1)
    aiosch.add_job(_db_backup, args=[bot], trigger='cron', hour=0, minute=1)
    aiosch.add_job(reset_prices, args=[bot], trigger='cron', hour=9, minute=0)

    aiosch.add_job(_salary_control, args=[bot], trigger='cron', hour=6, minute=0)
    aiosch.add_job(_salary_control, args=[bot], trigger='cron', hour=12, minute=0)
    aiosch.add_job(_salary_control, args=[bot], trigger='cron', hour=18, minute=0)

    aiosch.start()


async def _reset_tpay_available(bot: Bot):
    await service.reset_tpay_available()
    await bot.send_message(
        chat_id=glob.rms.group_chat_id,
        text=glob.RESET_TPAY_AVAILABLE_DONE
    )


async def _db_backup(bot: Bot):
    await bot.send_document(
        chat_id=glob.rms.db_backup_chat_id,
        document=FSInputFile(glob.rms.db_file_path)
    )
    await bot.send_message(
        chat_id=glob.rms.group_chat_id,
        text=glob.DB_BACKUP_DONE
    )


async def _salary_control(bot: Bot):
    lsp = await repo.get_last_salary_payout()

    # next cases mean that something must have gone wrong in the database records
    if lsp is None:
        raise RuntimeError('No last salary payout found!')
    if lsp.plan_date.weekday() != 0:
        raise RuntimeError('The last salary payout is not Monday!')

    # if the last salary payout from db is not paid out
    # and we passed the date of the last salary payout (or today is the payout day)
    # then we pay out the salaries
    if not lsp.paid_out and lsp.plan_date.date() <= datetime.now().date():
        await payout_salaries(lsp.plan_date)
        await bot.send_message(
            chat_id=glob.rms.group_chat_id,
            text=glob.SALARIES_PAID_OUT
        )

    # if the next payout is not present in db
    # then we create and insert it into db
    next_monday = datetime.now() + timedelta(days=7 - datetime.now().weekday())
    if lsp.plan_date.date() != next_monday.date():
        next_monday_plan = lsp.plan_date + timedelta(days=7 - lsp.plan_date.weekday())
        await repo.insert_salary_payout(SalaryPayout(
            plan_date=next_monday_plan.strftime(glob.DATETIME_FORMAT)
        ))
