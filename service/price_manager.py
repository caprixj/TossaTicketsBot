import random
import math
from datetime import datetime, timedelta

import aiofiles
import yaml
from aiogram import Bot

from model.database.dynprices import RateReset
from model.types.gem_counting_mode import GemCountingMode
from resources import glob, funcs
from resources.glob import MAX_FLUCT, MIN_FLUCT, FLUCT_GAUSS_SIGMA, INFL_ALPHA, \
    INIT_TPOOL, GEM_FREQ_YAML_PATH, MIN_DELTA_GEM_RATE, MAX_DELTA_GEM_RATE, GEM_BASE_PRICE
from resources.funcs import get_current_datetime, strdate
from repository import repository_core as repo
from service import service_core as service


async def reset_prices(bot: Bot = None):
    lpr = await repo.get_last_rate_history()

    # theoretically means something happened to the database records
    if lpr is None:
        raise RuntimeError('No last price reset found!')

    lpr_date = lpr.plan_date.date()

    # if somehow we're trying to reset already reset price for today
    if lpr_date == datetime.now().date():
        return

    updated_inflation = _get_updated_inflation(
        await service.get_tpool(infl=True)
    )
    updated_fluctuation = _get_updated_fluctuation(lpr.fluctuation)
    updated_rate = updated_inflation * updated_fluctuation
    diff = updated_rate / (lpr.inflation * lpr.fluctuation)

    await repo.reset_prices(diff)
    await repo.reset_artifact_investments(diff)
    await _reset_gem_rates(updated_rate)

    pr_days_dist = abs((datetime.now().date() - lpr.plan_date.date()).days)
    await repo.expand_price_history()
    await repo.insert_rate_history(RateReset(
        inflation=updated_inflation,
        fluctuation=updated_fluctuation,
        plan_date=strdate(lpr.plan_date + timedelta(days=pr_days_dist)),
        fact_date=get_current_datetime()
    ))

    if bot:
        text = f"{glob.RATE_RESET_TEXT}: {'+' if diff - 1 > 0 else ''}{(diff - 1) * 100:.2f}%"
        await funcs.broadcast_message(bot, text)


def _get_updated_fluctuation(last_fluctuation: float) -> float:
    g = random.gauss(1, FLUCT_GAUSS_SIGMA)
    upd_f = last_fluctuation * g

    gauss_distr = abs(random.gauss(0, FLUCT_GAUSS_SIGMA))
    if upd_f > MAX_FLUCT:
        upd_f = MAX_FLUCT - gauss_distr
    elif upd_f < MIN_FLUCT:
        upd_f = MIN_FLUCT + gauss_distr

    return upd_f


def _get_updated_inflation(tpool: float) -> float:
    return 1 + INFL_ALPHA * math.log(tpool / 100 / INIT_TPOOL)


async def _reset_gem_rates(updated_rate: float):
    async with aiofiles.open(GEM_FREQ_YAML_PATH, 'r', encoding='utf-8') as f:
        gem_freqs = yaml.safe_load(await f.read())

    mpool_gem_counts = await service.get_mpool_gc(GemCountingMode.RATES)
    mpool = sum(count for name, count in mpool_gem_counts.items())
    delta_freq = {
        name: count / mpool / gem_freqs[name]
        for name, count in mpool_gem_counts.items()
    }

    for name, df in delta_freq.items():
        fluct = random.uniform(0.98, 1.02)
        gem_price = GEM_BASE_PRICE * updated_rate * fluct

        if df < MIN_DELTA_GEM_RATE:
            updated_price = round(gem_price / MIN_DELTA_GEM_RATE, 7)
        elif df > MAX_DELTA_GEM_RATE:
            updated_price = round(gem_price / MAX_DELTA_GEM_RATE, 7)
        else:
            updated_price = round(gem_price / df, 7)

        await repo.reset_gem_rate(name, updated_price)
