from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from aiogram import Bot
from pytz import utc

from model.database.jobs import SalaryPayout
from utils import funcs
from service import service_core as service, price_manager
from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import resources.glob as glob
from repository import repository_core as repo

aiosch = AsyncIOScheduler(timezone=utc)


async def schedule(bot: Bot):
    # Database Backup
    aiosch.add_job(_db_backup, args=[bot], trigger='cron', hour=0, minute=1)
    aiosch.add_job(_db_backup, args=[bot], trigger='cron', hour=12, minute=1)

    # Daily Schedule (without tbox-available reset)
    aiosch.add_job(daily_sched, args=[bot], trigger='cron', hour=0, minute=1)

    # Tbox-Available Reset
    def get_kyiv_hour() -> Optional[int]:
        kyiv_now = datetime.now(ZoneInfo('Europe/Kyiv'))
        if kyiv_now.tzname() == 'EET':
            return 22
        elif kyiv_now.tzname() == 'EEST':
            return 21
        else:
            raise RuntimeError('No kyiv hour found!')

    aiosch.add_job(_tbox_reset, args=[bot], trigger='cron', hour=get_kyiv_hour(), minute=0)

    # Updates Checkup (every hour)
    for h in range(0, 23):
        aiosch.add_job(daily_sched, args=[bot], trigger='cron', hour=h, minute=0)

    aiosch.start()


async def daily_sched(bot: Bot = None, tbox: bool = False):
    lds = await repo.get_last_daily_schedule_date()

    # next cases mean that something must have gone wrong in the database records
    if lds is None:
        raise RuntimeError('No last daily schedule found!')

    # if the last daily schedule from db is today,
    # then we skip the update
    if datetime.now(timezone.utc).date() == lds.date():
        return

    if tbox:
        await _tbox_reset(bot)

    await service.reset_tpay_available()
    await price_manager.reset_prices(bot)
    # await service.payout_profits()  # (!) disabled artifact payouts
    await _salary_control()
    await _expire_mat_orders()

    await repo.insert_daily_schedule(date=funcs.utcnow_str())

    if bot:
        text = f'*{glob.DAILY_SCHEDULE_DONE}*'
        await funcs.broadcast_message(bot, text, chats=True)


async def _db_backup(bot: Bot):
    await bot.send_document(
        chat_id=glob.rms.db_backup_chat_id,
        document=FSInputFile(glob.rms.db_file_path)
    )


async def _tbox_reset(bot: Bot):
    await service.reset_tbox_available()

    text = f'*{glob.TBOX_RESET_DONE}*'
    await funcs.broadcast_message(bot, text, chats=True)


async def _expire_mat_orders():
    await repo.expire_material_orders()


async def _salary_control():
    lsp = await repo.get_last_salary_payout()

    # next cases mean that something must have gone wrong in the database records
    if lsp is None:
        raise RuntimeError('No last salary payout found!')
    if lsp.plan_date.weekday() != 0:
        raise RuntimeError('The last salary payout is not Monday!')

    # if the last salary payout from db is not paid out
    # and we passed the date of the last salary payout (or today is the payout day),
    # then we pay out the salaries
    if not lsp.paid_out and lsp.plan_date.date() <= datetime.now(timezone.utc).date():
        await service.payout_salaries(lsp.plan_date)

    # if the next payout is not present in db,
    # then we create and insert it into db
    next_monday = datetime.now(timezone.utc) + timedelta(days=7 - datetime.now(timezone.utc).weekday())
    if lsp.plan_date.date() != next_monday.date():
        next_monday_plan = lsp.plan_date + timedelta(days=7 - lsp.plan_date.weekday())
        await repo.insert_salary_payout(SalaryPayout(
            plan_date=next_monday_plan.strftime(glob.UTC_FORMAT)
        ))
