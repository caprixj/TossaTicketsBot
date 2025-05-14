import math
import random
import re
from datetime import datetime

import aiofiles
import yaml
from aiogram.types import Message

from model.database import Material
from model.database.member import Member
from resources.const.glob import UNI_TAX as F, MIN_FEE as M, DATETIME_FORMAT, MATERIALS_YAML_PATH


def get_current_datetime() -> str:
    return datetime.now().strftime(DATETIME_FORMAT)


def strdate(date: datetime) -> str:
    return date.strftime(DATETIME_FORMAT)


async def get_fee(transfer: float) -> float:
    return max(round(F * transfer, 2), M)


async def get_transfer_by_total(t: float) -> float:
    return t - M if F * (t - M) <= M else round(t / (F + 1), 2)


def get_formatted_name(member: Member, ping: bool = False) -> str:
    if member is None:
        return '/member is none/'

    parts = [member.first_name or '', member.last_name or '']
    name = str(' '.join(filter(None, parts)) or member.username or '-')

    return f"[{_escape_brackets(name)}](tg://user?id={member.user_id})" \
        if ping else _escape_markdown_v2(name)


def get_command(message: Message) -> str:
    return message.text.split()[0].split('@')[0].lstrip('/')


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


def _escape_markdown_v2(text: str) -> str:
    return re.sub(r'([_*])', r'\\\1', text)


def _escape_brackets(text: str) -> str:
    return text.replace('[', ' ').replace(']', ' ')
