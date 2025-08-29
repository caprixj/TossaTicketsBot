import traceback
from contextlib import asynccontextmanager
from typing import Union

from fastapi import FastAPI, APIRouter, Request, HTTPException
from pydantic import BaseModel

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from model.types import RunMode
from service import setup, scheduling
import resources.glob as glob
from middleware.activity_analyzer_middleware import ActivityAnalyzerMiddleware
from middleware.source_filter_middleware import SourceFilterMiddleware
from service.router_loader import get_routers

WEBHOOK_BASE_URL = "https://example.com"
WEBHOOK_PATH = "/telegram/webhook"  # public endpoint path

api = APIRouter(prefix="/api")
tg = APIRouter()


class SetWebhookBody(BaseModel):
    base_url: str


def get_bot(app: FastAPI) -> Bot:
    bot: Union[Bot, None] = app.state.bot
    if not bot:
        raise HTTPException(status_code=503, detail="Bot is not ready")
    return bot


def get_dp(app: FastAPI) -> Dispatcher:
    return app.state.dp


@api.get("/health")
async def health():
    return {"status": "ok"}


@api.post("/dev/set_webhook")
async def dev_set_webhook(data: SetWebhookBody, request: Request):
    bot = get_bot(request.app)
    target = data.base_url.rstrip("/") + WEBHOOK_PATH

    await bot.set_webhook(
        url=target,
        drop_pending_updates=True,
        secret_token=None
    )

    return {"ok": True, "webhook": target}


@tg.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    app: FastAPI = request.app
    bot = get_bot(app)
    dp = get_dp(app)

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    try:
        update = types.Update.model_validate(payload)
        await dp.feed_update(bot, update)
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        raise HTTPException(status_code=202)

    return {"ok": True}


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_mode = setup.define_run_mode()
    valid_args = setup.define_rms(run_mode)

    if not valid_args:
        raise RuntimeError(glob.INVALID_ARGS)

    await setup.create_databases()

    dp = Dispatcher()
    bot = Bot(
        token=glob.rms.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )

    for router in get_routers():
        dp.include_router(router)

    dp.message.middleware(ActivityAnalyzerMiddleware())
    dp.message.middleware(SourceFilterMiddleware())

    await scheduling.schedule(bot)

    app.state.bot = bot
    app.state.dp = dp

    if run_mode == RunMode.PROD:
        target = glob.rms.host_url.rstrip('/') + WEBHOOK_PATH
        await bot.set_webhook(
            url=target,
            drop_pending_updates=True,
            secret_token=None
        )

    try:
        yield
    finally:
        await bot.session.close()


def create_app() -> FastAPI:
    app = FastAPI(title="Bot Webhook API", lifespan=lifespan)
    app.include_router(api)
    app.include_router(tg)
    return app
