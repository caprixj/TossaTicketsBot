from aiogram import Bot

from service import service_core as service
from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import resources.const.glob as glob

scheduler = AsyncIOScheduler()


async def reset_tpay_available(bot: Bot):
    await service.reset_tpay_available()
    await bot.send_message(
        chat_id=glob.rms.group_chat_id,
        text=glob.RESET_TPAY_AVAILABLE_DONE
    )


async def db_backup(bot: Bot):
    await bot.send_document(
        chat_id=glob.rms.db_backup_chat_id,
        document=FSInputFile(glob.rms.db_file_path)
    )
    await bot.send_message(
        chat_id=glob.rms.group_chat_id,
        text=glob.DB_BACKUP_DONE
    )


async def schedule(bot: Bot):
    scheduler.add_job(reset_tpay_available, args=[bot], trigger='cron', hour=0, minute=1, misfire_grace_time=3600)
    scheduler.add_job(db_backup, args=[bot], trigger='cron', hour=0, minute=1, misfire_grace_time=3600)
    scheduler.start()
