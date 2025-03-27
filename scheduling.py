from copula import service
from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import resources.const.glob as glob


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


async def schedule(scheduler: AsyncIOScheduler):
    scheduler.add_job(reset_tpay_available, 'cron', hour=0, minute=1, misfire_grace_time=3600)
    scheduler.add_job(db_backup, 'cron', hour=0, minute=1, misfire_grace_time=3600)
    scheduler.start()
