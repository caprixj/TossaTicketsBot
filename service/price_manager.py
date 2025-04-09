import random
import math
from datetime import datetime, timedelta

from aiogram import Bot

from model.database.price_reset import PriceReset
from resources.const import glob
from resources.const.glob import MAX_FLUCTUATION, MIN_FLUCTUATION, FLUCTUATION_GAUSS_SIGMA, INFLATION_ALPHA, \
    INITIAL_TPOOL
from resources.funcs.funcs import get_current_datetime, date_to_str
from repository import repository_core as repo


async def adjust_tickets_amount(price: float, inflation: bool = True) -> float:
    lpr = await repo.get_last_price_reset()

    if lpr is None:
        raise RuntimeError('No last price reset found!')

    if inflation:
        return price * lpr.fluctuation * lpr.inflation
    else:
        return price * lpr.fluctuation


async def p_adjust_tickets_amount(price: float) -> (float, float, float):
    lpr = await repo.get_last_price_reset()

    if lpr is None:
        raise RuntimeError('No last price reset found!')

    return price * lpr.inflation * lpr.fluctuation, lpr.inflation, lpr.fluctuation


async def reset_prices(bot: Bot):
    tpool = await repo.get_total_tickets()

    while True:
        lpr = await repo.get_last_price_reset()

        # theoretically means something happened to the database records
        if lpr is None:
            raise RuntimeError('No last price reset found!')

        lpr_date = lpr.plan_date.date()
        yesterday_date = (datetime.now() - timedelta(days=1)).date()

        # if somehow we're trying to reset already reset price for today
        if lpr_date == datetime.now().date():
            continue

        updated_fluctuation = _get_updated_fluctuation(lpr.fluctuation)
        updated_inflation = _get_updated_inflation(tpool, lpr.inflation)

        await repo.insert_price_history(PriceReset(
            inflation=updated_inflation,
            fluctuation=updated_fluctuation,
            plan_date=date_to_str(lpr.plan_date + timedelta(days=1)),
            fact_date=get_current_datetime()
        ))

        # we're resetting prices for each skipped day
        # the skip may happen due to the temporal bot's inactivity
        if lpr_date == yesterday_date:
            break

    await bot.send_message(
        chat_id=glob.rms.group_chat_id,
        text=glob.PRICE_RESET_DONE
    )


def _get_updated_fluctuation(last_fluctuation: float) -> float:
    g = random.gauss(1, FLUCTUATION_GAUSS_SIGMA)
    upd_f = last_fluctuation * g

    gauss_distribution = abs(random.gauss(0, FLUCTUATION_GAUSS_SIGMA))
    if upd_f > MAX_FLUCTUATION:
        upd_f = MAX_FLUCTUATION - gauss_distribution
    elif upd_f < MIN_FLUCTUATION:
        upd_f = MIN_FLUCTUATION + gauss_distribution

    return upd_f


def _get_updated_inflation(tpool: float, last_inflation: float) -> float:
    return last_inflation * (1 + INFLATION_ALPHA * math.log(tpool / INITIAL_TPOOL))
