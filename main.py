import asyncio
import logging
import sys
from typing import Union

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import setup
import scheduling
import resources.const.glob as glob
from middleware.activity_analyzer_middleware import ActivityAnalyzerMiddleware
from middleware.source_filter_middleware import SourceFilterMiddleware

from router_loader import get_routers

dp = Dispatcher()
for router in get_routers():
    dp.include_router(router)

bot: Union[Bot, None] = None


async def main():
    global bot
    run_mode = setup.define_run_mode()
    valid_args = setup.define_rms(run_mode)

    if not valid_args:
        raise RuntimeError(glob.INVALID_ARGS)

    await setup.create_databases()

    bot = Bot(
        token=glob.rms.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN
        )
    )

    dp.message.middleware(ActivityAnalyzerMiddleware())
    dp.message.middleware(SourceFilterMiddleware())

    await scheduling.schedule(bot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
