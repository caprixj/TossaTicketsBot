import asyncio
import math
import random
import re
from datetime import datetime, timezone
from typing import Union
from zoneinfo import ZoneInfo

import aiofiles
import yaml
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramAPIError
from aiogram.types import Message

from model.database import Material
from model.database.member import Member, DelMember
from resources import glob
from resources.glob import SINGLE_TAX as F, MIN_SINGLE_TAX as M, UTC_FORMAT, MATERIALS_YAML_PATH, UI_DATETIME_FORMAT


async def broadcast_message(
    bot: Bot, text: str,
    rate_limit: float = 0.05,  # 20 messages/sec
    chats: bool = False,
    admins: bool = False
):
    if not (chats or admins):
        raise ValueError('def broadcast_message: destination has not been set')

    destinations = []
    if chats:
        destinations.extend(glob.rms.get_broadcasting_chats())
    if admins:
        destinations.extend(glob.rms.get_admin_ids())

    for d in destinations:
        try:
            await bot.send_message(chat_id=d, text=text)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            await bot.send_message(chat_id=d, text=text)
        except TelegramAPIError as err:
            print(f'Failed to send to {d}: {err}')

        await asyncio.sleep(rate_limit)


def utcnow_str() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime(UTC_FORMAT)


def to_iso_z(dt: datetime) -> str:
    if dt.tzinfo is None:
        raise ValueError('Naive datetime passed to to_iso_z(dt: datetime) -> str')
    return dt.astimezone(timezone.utc).replace(microsecond=0).strftime(UTC_FORMAT)


def to_utc(iso_utc: str) -> datetime:
    # if python v3.11+
    # return datetime.fromisoformat(iso_utc).astimezone(timezone.utc).replace(microsecond=0))
    return (datetime
            .fromisoformat(iso_utc.replace('Z', '+00:00'))
            .astimezone(timezone.utc)
            .replace(microsecond=0))

def to_kyiv_str(iso_utc: str) -> str:
    dt = datetime.fromisoformat(iso_utc.replace('Z', '+00:00'))

    if dt.tzinfo is None:
        raise ValueError('Naive datetime passed to to_kyiv_time_str(iso_utc: str) -> str')

    dt_local = dt.astimezone(ZoneInfo('Europe/Kyiv')).replace(microsecond=0)
    return f'{dt_local.strftime(UI_DATETIME_FORMAT)} (Kyiv)'


def to_utc_str(dt: datetime) -> str:
    if dt.tzinfo is None:
        raise ValueError('Naive datetime passed to to_kyiv_time_str(iso_utc: str) -> str')

    dt_local = dt.astimezone(timezone.utc).replace(microsecond=0)
    return f'{dt_local.strftime(UI_DATETIME_FORMAT)} (UTC)'


async def get_single_tax(transfer: int) -> int:
    return max(round(F * transfer), M)


async def get_transfer_by_total(t: int) -> int:
    return t - M if F * (t - M) <= M else round(t / (F + 1))


def get_formatted_name(member: Union[Member, DelMember], ping: bool = False) -> str:
    if member is None:
        return '[not found]'

    parts = [member.first_name or '', member.last_name or '']
    name = str(' '.join(filter(None, parts)) or member.username or '-')

    return f"[{_escape_brackets(name)}](tg://user?id={member.user_id})" \
        if ping else _escape_markdown_v2(name)


def get_command(message: Message) -> str:
    return (message.text or '').split()[0].split('@')[0].lstrip('/')


async def get_materials_yaml() -> list[Material]:
    async with aiofiles.open(MATERIALS_YAML_PATH, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(await f.read())

    return [
        Material(
            name=item['name'],
            emoji=item['emoji']
        ) for item in data
    ]


def perturb_probs(probs: dict[str, float], sigma: float) -> list[float]:
    noises = [
        math.exp(random.gauss(-0.5 * sigma ** 2, sigma))
        for _ in probs
    ]

    weighted = [p * x for p, x in zip(probs.values(), noises)]
    total = sum(weighted)
    return [round(w / total, 5) for w in weighted]


def all_unique_or_none(li: list[str]) -> bool:
    strings = [s for s in li if s is not None]
    return len(strings) == len(set(strings))


def _escape_markdown_v2(text: str) -> str:
    return re.sub(r'([_*])', r'\\\1', text)


def _escape_brackets(text: str) -> str:
    return text.replace('[', ' ').replace(']', ' ')
