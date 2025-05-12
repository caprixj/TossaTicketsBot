import random
import math
from datetime import datetime, timedelta

import aiofiles
import yaml
from aiogram import Bot

from model.database.dynprices import RateReset
from resources.const import glob
from resources.const.glob import MAX_FLUCT, MIN_FLUCT, FLUCT_GAUSS_SIGMA, INFL_ALPHA, \
    INIT_TPOOL, GEM_FREQ_YAML_PATH, MIN_DELTA_GEM_RATE, MAX_DELTA_GEM_RATE, GEM_BASE_PRICE
from resources.funcs.funcs import get_current_datetime, strdate
from repository import repository_core as repo
from service import service_core as service


async def reset_prices(bot: Bot = None):
    lpr = await repo.get_last_price_reset()

    # theoretically means something happened to the database records
    if lpr is None:
        raise RuntimeError('No last price reset found!')

    lpr_date = lpr.plan_date.date()

    # if somehow we're trying to reset already reset price for today
    if lpr_date == datetime.now().date():
        return

    pr_days_dist = abs((datetime.now().date() - lpr.plan_date.date()).days)
    total_tpool = await service.get_tpool()
    updated_inflation = _get_updated_inflation(total_tpool)
    updated_fluctuation = _get_updated_fluctuation(lpr.fluctuation)
    updated_rate = updated_inflation * updated_fluctuation
    diff = updated_rate / (lpr.inflation * lpr.fluctuation)

    await repo.reset_prices(diff)
    await repo.reset_artifact_values(diff)
    await _reset_gem_rates(updated_rate)

    await repo.expand_price_history()
    await repo.insert_rate_history(RateReset(
        inflation=updated_inflation,
        fluctuation=updated_fluctuation,
        plan_date=strdate(lpr.plan_date + timedelta(days=pr_days_dist)),
        fact_date=get_current_datetime()
    ))

    await bot.send_message(
        chat_id=glob.rms.main_chat_id,
        text=f'{glob.PRICE_RESET_DONE}\n'
             f'{glob.RATE_RESET_TEXT}: {"+" if diff - 1 > 0 else str()}{(diff - 1) * 100:.2f}%'
    )


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
    return 1 + INFL_ALPHA * math.log(tpool / INIT_TPOOL)


async def _reset_gem_rates(updated_rate: float):
    async with aiofiles.open(GEM_FREQ_YAML_PATH, 'r', encoding='utf-8') as f:
        gem_freqs = yaml.safe_load(await f.read())

    mpool_gem_counts = await service.get_mpool_gem_counts()
    mpool = sum(count for name, count in mpool_gem_counts.items())
    delta_freq = {
        name: count / mpool / gem_freqs[name]
        for name, count in mpool_gem_counts.items()
    }

    for name, df in delta_freq.items():
        fluct = random.uniform(0.98, 1.02)
        gem_price = GEM_BASE_PRICE * updated_rate * fluct
        if df < MIN_DELTA_GEM_RATE:
            await repo.reset_gem_rate(name, gem_price / MIN_DELTA_GEM_RATE)
        elif df > MAX_DELTA_GEM_RATE:
            await repo.reset_gem_rate(name, gem_price / MAX_DELTA_GEM_RATE)
        else:
            await repo.reset_gem_rate(name, gem_price / df)
