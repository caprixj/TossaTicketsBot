import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import setup
import scheduling
import copula
import resources.const.glob as glob
from middleware.source_filter_middleware import SourceFilterMiddleware
from service.service_core import Service

from router_loader import get_routers

for router in get_routers():
    copula.dp.include_router(router)


async def main():
    run_mode = setup.define_run_mode()
    valid_args = setup.define_rms(run_mode)
    scheduler = AsyncIOScheduler()

    if not valid_args:
        raise RuntimeError(glob.INVALID_ARGS)

    copula.service = Service(glob.rms.db_file_path)
    await setup.create_databases()

    copula.service.bot = Bot(
        token=glob.rms.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN
        )
    )

    copula.dp.message.middleware(SourceFilterMiddleware())

    await scheduling.schedule(scheduler)
    await copula.dp.start_polling(copula.service.bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
